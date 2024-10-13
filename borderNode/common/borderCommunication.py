import os
import signal
from internalCommunication.internalCommunication import InternalCommunication
import zmq
import logging
from entryParsing.common.utils import initializeLog

PREFETCH_COUNT = 1 # break round robin
DELIVERY_MODE = 1 # make message transient, es lo mismo por ahora
PRINT_FREQUENCY = 1000
class BorderNodeCommunication:
    def __init__(self):
        initializeLog()
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        socket.bind("tcp://*:5556")
        self._clientSocket = socket
        self._clientSocket.setsockopt(zmq.RCVTIMEO, 100)
        # dispatcher
        self._internalCommunication = InternalCommunication(os.getenv('RESP_DISP'), os.getenv('NODE_ID'))
        self._accepterCommunication = InternalCommunication()
        self._running = True

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.sendClient)

    def stop(self, _signum, _):
        self._running = False
        self._internalCommunication.stop()
        self._accepterCommunication.stop()
        #self._clientSocket.close()
        
    def closeClientSocket(self):
        self._clientSocket.close()

    def isRunning(self):
        return self._running

    def receiveFromClient(self):
        try:
            msg = self._clientSocket.recv()
        except:
            msg = None
        return msg
    
    def sendClient(self, ch, method, properties, body):
        if not self.isRunning():
            return
        self._clientSocket.send(body)
        logging.info(f'action: sending query info to client | result: success')
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def sendInitializer(self, message: bytes):
        self._accepterCommunication.sendToInitializer(message)
 