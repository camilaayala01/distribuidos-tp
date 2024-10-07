import pika
import signal
import os
from internalCommunication.internalCommunication import InternalCommunication
import zmq
#from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber

PREFETCH_COUNT = 1 # break round robin
DELIVERY_MODE = 1 # make message transient, es lo mismo por ahora

class BorderNodeCommunication:
    def __init__(self):
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        socket.bind("tcp://*:5556")
        self._clientSocket = socket
        # dispatcher
        self._internalCommunication = InternalCommunication(os.getenv('RESP_DISP'), os.getenv('NODE_ID'))
        self._accepterCommunication = InternalCommunication("Accepter")
        print("about to define messagehandler")

    def execute(self):
        print("establezco handler")
        self._internalCommunication.defineMessageHandler(self.sendClient)

    def receiveFromClient(self):
        msg = self._clientSocket.recv()
        print("received msg from client")
        return msg
    
    def sendClient(self, ch, method, properties, body):
        print("EL CLIENTE VA A RECIBIR ALGOOOO")
        self._clientSocket.send(body)
        print("SE MANDO LA QUERYYYY ")
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def sendInitializer(self, message: bytes):
        print("sending to initializer")
        self._accepterCommunication.sendToInitializer(message)
 