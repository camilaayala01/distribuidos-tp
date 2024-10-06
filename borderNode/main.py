import time
from threading import Thread
from common.borderCommunication import BorderNodeCommunication

def listenForClient(communication):
    end = False
    while end != True:
        msg = communication.receiveFromClient()
        if msg.decode() == "END":
            end = True

        communication.sendInitializer(msg)

        time.sleep(1)

def main():
    print("corriendo")
    communication = BorderNodeCommunication()
    Thread(target=listenForClient, args=[communication]).run()

if __name__ == "__main__":
    main()