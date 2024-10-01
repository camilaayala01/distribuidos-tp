import os
import zmq
import time
from threading import Thread
from ..internalCommunication.internalComunication import InternalCommunication

class ResponseDispatcher:
    def __init__(self, socket): 
        self._internalComunnication = InternalCommunication(os.getenv('RESP_DISP'), os.getenv('NODE_ID'))
        self._socket = socket

    def handleMessage(self, ch, method, properties, body):
        self._socket.send(body)
    
    def execute(self):
        self._internalComunnication.defineMessageHandler(self.handleMessage)


def ClientAccepter(socket):
    end = False
    while end != True:
        msg = socket.recv() 
        # sendToInitializer()

        # Streams in ZMQ are received as bytes. 
        # Cast the msg to string and decode it to be able to do the comparison
        if msg.decode() == "END":
            end = True

        time.sleep(1)


def main():
    port = "5556"
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://*:%s" % port)

    Thread(target=ClientAccepter, args=[socket]).run()

    ResponseDispatcher(socket).execute()