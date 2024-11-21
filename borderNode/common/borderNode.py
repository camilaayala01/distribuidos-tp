import os
import threading
import time
import uuid

from entryParsing.common.table import Table
from .activeClients import ActiveClients
from entryParsing.common.clientHeader import ClientHeader
from entryParsing.common.messageType import MessageType
from internalCommunication.internalMessageType import InternalMessageType
from .borderCommunication import BorderNodeCommunication

# do heartbeat when receiving a disconnect event and also when booting (or rebooting)
# what happens if border node fails after receiving a zmq message, before sending it to initializer?
# option 1: implement stop and wait mechanism
# option 2: change queues to rabbit, using subscriptions (exchange) for acks and responses, 
# and queue for data transfer
class BorderNode: 
    def __init__(self):
        self._communication = BorderNodeCommunication()
        self._activeClients = ActiveClients()
        # only one thread will actually change it, but just in case
        self._timeLock = threading.Lock()
        self._currentTimer = time.perf_counter()
    
    def stop(self, _signum, _):
        self._communication.stop()
        self._activeClients.removeClientFiles()

    def handleHandshake(self, clientId: bytes):
        assignedId = uuid.uuid4().bytes
        self._activeClients.storeNewClient(assignedId)
        self._communication.sendToClient(clientId, MessageType.CONNECT_ACCEPT.serialize() + assignedId)
    
    def handleDataMessage(self, clientId: bytes, msg: bytes):
        if not self._activeClients.isActiveClient(clientId):
            self._communication.sendToClient(clientId=clientId, data=MessageType.CONNECT_RETRY.serialize())
            return
        self._activeClients.setTimestampForClient(clientId)        
        header, _ = ClientHeader.deserialize(msg)
        if header.isLastClientPacket():
            print("received last packet!")
            self._activeClients.removeClientsFromActive({clientId})
            # ack after deleting, and in deletion confirmation packet, ack after checking
        self._communication.sendInitializer(InternalMessageType.DATA_TRANSFER.serialize() + clientId + msg)
    
    def handleClientMessage(self, clientId: bytes, data: bytes):
        try:
            type, msg = MessageType.deserialize(data)
        except:
            # wont happen unless client is corrupt
            self._communication.sendToClient(clientId=clientId, data=MessageType.FORMAT_ERROR.serialize())
            return
        
        match type:
            case MessageType.CONNECT:
                return self.handleHandshake(clientId)
            case MessageType.DATA_TRANSFER:
                return self.handleDataMessage(clientId=clientId, msg=msg)

    def handleTimeoutSignal(self, _signum, _):
        self._currentTimer, expired = self._activeClients.getExpiredTimers(lastTimer=self._currentTimer)
        for clientId in expired:
            print(f"oops, client {clientId} expired :( so sad for him")
            self._communication.sendInitializer(InternalMessageType.CLIENT_FLUSH.serialize() + clientId)
        self._activeClients.removeClientsFromActive(expired)

    def listenForClient(self):
        while self._communication.isRunning():
            received = self._communication.receiveFromClient()
            if received is None:
                continue
            id, data = received
            self.handleClientMessage(id, data)
        self._communication.closeClientSocket()

    # establecer timer que salte cada equis cantidad de tiempo y revise los ultimos timestamps
    # me olvido de toda esta parte del monitor, y cuando ese timer salta, desconecto a todos
    # los q no me mandaron nada: quizas puedo avisarles pero meh. 
    # Para los clientes a los que le acabo d asignar un ID, guardo el timestamp del heartbeat 
    # (posterior al store en disco, o incluso al envio del cliente). 
    # los active clients dejan de ser active clients, deberian ser tipo sender clients o alguna
    # re pelotudez asi, tipo los clients q están mandando información. cuando les tengo q mandar 
    # yo, ya no es mi problema guardar que estaba activo.
    # 
    # lo unico persistente en disco son los ids d clientes: los borro de active cuando me llega
    # el eof de reviews
    # vamos a seguir teniendo q hacer stop and wait, primero x esto del eof y segundo x si se 
    # cae el border

    def dispatchResponses(self):
        self._communication.executeDispatcher()