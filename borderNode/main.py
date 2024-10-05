import time
from threading import Thread
from borderNodeCommunication import BorderNodeCommunication
from internalCommunication import InternalCommunication

def listenForClient(communication):
    end = False
    while end != True:
        msg = communication.receiveFromClient()
        if msg.decode() == "END":
            end = True

        communication.sendInitializer(msg)

        time.sleep(1)

def main():
    communication = BorderNodeCommunication()
    Thread(target=listenForClient, args=[communication]).run()
