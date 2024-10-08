import os
from internalCommunication.internalCommunication import InternalCommunication
import zmq
import logging
from entryParsing.common.utils import initializeLog

PREFETCH_COUNT = 1 # break round robin
DELIVERY_MODE = 1 # make message transient, es lo mismo por ahora

class BorderNodeCommunication:
    def __init__(self):
        initializeLog()
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        socket.bind("tcp://*:5556")
        self._clientSocket = socket
        # dispatcher
        self._internalCommunication = InternalCommunication(os.getenv('RESP_DISP'), os.getenv('NODE_ID'))
        self._accepterCommunication = InternalCommunication()

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.sendClient)

    def receiveFromClient(self):
        msg = self._clientSocket.recv()
        logging.info(f'action: receiving batch from client | result: success')
        return msg
    
    def sendClient(self, ch, method, properties, body):
        self._clientSocket.send(body)
        logging.info(f'action: sending query info to client | result: success')
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def sendInitializer(self, message: bytes):
        self._accepterCommunication.sendToInitializer(message)
        logging.info(f'action: sending batch to initializer | result: success')
 