import os
import uuid
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.common.messageType import MessageType
from internalCommunication.internalCommunication import InternalCommunication
import zmq
import logging
from entryParsing.common.utils import initializeLog
from internalCommunication.internalMessageType import InternalMessageType

PRINT_FREQUENCY = 1000

class BorderNodeCommunication:
    def __init__(self):
        initializeLog()
        context = zmq.Context()
        socket = context.socket(zmq.ROUTER)
        socket.bind("tcp://*:5556") #TODO: SACAR HARDCODEO
        self._clientSocket = socket
        self._clientSocket.setsockopt(zmq.RCVTIMEO, 1000) #TODO: PENSARLO
        self._clientSocket.setsockopt(zmq.HEARTBEAT_IVL, 1000)
        self._monitor = self._clientSocket.get_monitor_socket()
        # dispatcher
        self._internalCommunication = InternalCommunication(os.getenv('DISP'))
        self._accepterCommunication = InternalCommunication()
        self._running = True
    
    def executeDispatcher(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def stop(self):
        self._running = False
        self._internalCommunication.stop()
        self._accepterCommunication.stop()
        
    def closeClientSocket(self):
        self._clientSocket.disable_monitor()
        self._clientSocket.close()

    def isRunning(self):
        return self._running

    def receiveFromClient(self):
        try:
            return self._clientSocket.recv_multipart()
        except zmq.Again:
            return None
        # any other exception must be thrown

    def sendToClient(self, clientId, data):
        self._clientSocket.send_multipart([clientId, data])
    
    def sendQueryToClient(self, body):
        if not self.isRunning():
            return
        header, _ = HeaderWithQueryNumber.deserialize(body)
        self.sendToClient(clientId=header.getClient(), data=MessageType.QUERY_RESPONSE.serialize() + body)
        logging.info(f'action: sending query info to client | result: success')

    # TODO modularize this handle message
    def handleMessage(self, ch, method, _properties, body):
        if not self.isRunning():
            return
        msgType, msg = InternalMessageType.deserialize(body)
        match msgType:
            case InternalMessageType.DATA_TRANSFER:
                self.sendQueryToClient(msg)
            case InternalMessageType.CLIENT_FLUSH:
                logging.info(f'action: receive client flush | client id: {msg}')
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def sendInitializer(self, message: bytes):
        self._accepterCommunication.sendToInitializer(message)
 