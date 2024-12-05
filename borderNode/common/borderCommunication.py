import zmq
from entryParsing.common.utils import initializeLog
from threading import Lock
import os

class BorderNodeCommunication:
    def __init__(self):
        initializeLog()
        context = zmq.Context()
        socket = context.socket(zmq.ROUTER)
        socket.bind(f"tcp://*:{os.getenv('CLIENT_PORT')}") 
        self._clientSocket = socket
        self._clientSocket.setsockopt(zmq.RCVTIMEO, 1000)
        self._clientSocket.setsockopt(zmq.HEARTBEAT_IVL, 1000)
        self._lock = Lock()

    def sendToClient(self, clientId, data):
        with self._lock:
            self._clientSocket.send_multipart([clientId, data])
        
    def stop(self):
        self._clientSocket.close()
        
    def closeClientSocket(self):
        self._clientSocket.close()

    def receiveFromClient(self):
        try:
            return self._clientSocket.recv_multipart()
        except zmq.Again:
            return None
        # any other exception must be thrown
 