import zmq
from entryParsing.common.utils import initializeLog

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

    def sendToClient(self, clientId, data):
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
 