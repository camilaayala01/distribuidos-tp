import threading
import time
import uuid
import zmq
import logging
from internalCommunication.internalCommunication import InternalCommunication
from .activeClients import ActiveClients
from entryParsing.headerInterface import ClientHeader
from entryParsing.common.messageType import MessageType
from entryParsing.common.fieldParsing import getClientIdUUID
from internalCommunication.internalMessageType import InternalMessageType
from .borderCommunication import BorderNodeCommunication
from healthcheckAnswerController.healthcheckAnswerController import HealthcheckAnswerController

class ClientAccepter: 
    def __init__(self, communication: BorderNodeCommunication, stopEvent: threading.Event):
        self._clientCommunication = communication
        self._currentTimer = time.perf_counter()
        self._activeClients = ActiveClients()
        # only one thread will actually change it, but just in case
        self._timeLock = threading.Lock()
        self._internalCommunication = InternalCommunication()
        self._healthcheckAnswerController = HealthcheckAnswerController()
        self._healthcheckAnswerController.execute()
        self._stopEvent = stopEvent

    def stop(self, _signum, _):
        self._stopEvent.set()
        self._healthcheckAnswerController.stop()
        self._internalCommunication.sendToDispatcher(InternalMessageType.SHUTDOWN.serialize())
        self._activeClients.removeClientFiles()
        self._clientCommunication.stop()
        self._internalCommunication.stop()

    def handleHandshake(self, clientId: bytes):
        assignedId = uuid.uuid4().bytes
        self._activeClients.storeNewClient(assignedId)
        self._clientCommunication.sendToClient(clientId, MessageType.CONNECT_ACCEPT.serialize() + assignedId)
    
    def sendAck(self, clientId: bytes, clientHeader: ClientHeader):
        self._clientCommunication.sendToClient(clientId=clientId, data=MessageType.MESSAGE_ACK.serialize() + clientHeader.serialize())

    def handleDataMessage(self, clientId: bytes, msg: bytes):
        if not self._activeClients.isActiveClient(clientId):
            self._clientCommunication.sendToClient(clientId=clientId, data=MessageType.CONNECT_RETRY.serialize())
            return
        self._activeClients.setTimestampForClient(clientId)        
        header, _ = ClientHeader.deserialize(msg)
        self._internalCommunication.sendToInitializer(InternalMessageType.DATA_TRANSFER.serialize() + clientId + msg)
        self.sendAck(clientId, header)
        if header.isLastClientPacket():
            self._activeClients.removeClientsFromActive({clientId})
    
    def handleEndOfDataTransfer(self, clientId: bytes):
        self._activeClients.removeClientsFromActive({clientId})
        self._clientCommunication.sendToClient(clientId=clientId, data=MessageType.ACK_END_OF_DATA.serialize())
    
    def handleClientMessage(self, clientId: bytes, data: bytes):
        try:
            type, msg = MessageType.deserialize(data)
        except:
            # wont happen unless client is corrupt
            self._clientCommunication.sendToClient(clientId=clientId, data=MessageType.FORMAT_ERROR.serialize())
            return
        
        match type:
            case MessageType.CONNECT:
                return self.handleHandshake(clientId=clientId)
            case MessageType.DATA_TRANSFER:
                return self.handleDataMessage(clientId=clientId, msg=msg)
            case MessageType.FINISH_DATA_TRANSFER:
                return self.handleEndOfDataTransfer(clientId=clientId)

    def handleTimeoutSignal(self, _signum, _):
        self._currentTimer, expired = self._activeClients.getExpiredTimers(lastTimer=self._currentTimer)
        for clientId in expired:
            logging.info(f"client {getClientIdUUID(clientId)} expired, starting flush")
            self._internalCommunication.sendToInitializer(InternalMessageType.CLIENT_FLUSH.serialize() + clientId)
        self._activeClients.removeClientsFromActive(expired)

    def listenForClient(self):
        while not self._stopEvent.is_set():
            try:
                received = self._clientCommunication.receiveFromClient()
                if received is None:
                    continue
                id, data = received
                self.handleClientMessage(id, data)
            except zmq.error.ZMQError:
                if self._stopEvent.is_set():
                    return
                break
        self.stop()