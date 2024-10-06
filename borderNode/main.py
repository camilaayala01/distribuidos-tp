import time
from threading import Thread
<<<<<<< HEAD
from borderNodeCommunication.borderNodeCommunication import BorderNodeCommunication
=======
from borderNodeCommunication import BorderNodeCommunication
from internalCommunication import InternalCommunication
>>>>>>> 9091c93b0e8d6bd323bd7b8bab0494e42aaf8561

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
