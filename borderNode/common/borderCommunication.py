import os
import uuid
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.common.messageType import MessageType
from internalCommunication.internalCommunication import InternalCommunication
import zmq
import logging
from entryParsing.common.utils import initializeLog

PRINT_FREQUENCY = 1000

class BorderNodeCommunication:
    def __init__(self):
        initializeLog()
        context = zmq.Context()
        socket = context.socket(zmq.ROUTER)
        socket.bind("tcp://*:5556") #TODO: SACAR HARDCODEO
        self._clientSocket = socket
        self._clientSocket.setsockopt(zmq.RCVTIMEO, 10000) #TODO: PENSARLO
        # dispatcher
        self._internalCommunication = InternalCommunication(os.getenv('DISP'))
        self._accepterCommunication = InternalCommunication()
        self._running = True

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.sendClient)

    def stop(self, _signum, _):
        self._running = False
        self._internalCommunication.stop()
        self._accepterCommunication.stop()
        
    def closeClientSocket(self):
        self._clientSocket.close()

    def isRunning(self):
        return self._running

    def receiveFromClient(self):
        try:
            id, data = self._clientSocket.recv_multipart()  
            type, msg = MessageType.deserialize(data)
            if type == MessageType.CONNECT:
                self._clientSocket.send_multipart([id, uuid.uuid4().bytes])
                return None
            return id + msg
        except:
            return None
    
    def sendClient(self, ch, method, _properties, body):
        if not self.isRunning():
            return
        header, _ = HeaderWithQueryNumber.deserialize(body)
        self._clientSocket.send_multipart([header.getClient(), body])
        logging.info(f'action: sending query info to client | result: success')
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def sendInitializer(self, message: bytes):
        self._accepterCommunication.sendToInitializer(message)
 