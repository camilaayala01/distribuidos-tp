from threading import Thread
from common.borderCommunication import BorderNodeCommunication
import signal

def listenForClient(communication):
    while True:
        msg = communication.receiveFromClient()
        if msg == "":
            break
        communication.sendInitializer(msg)

def main():
    communication = BorderNodeCommunication()
    signal.signal(signal.SIGTERM, communication.stop)
    thread = Thread(target=communication.execute)
    thread.start()
    listenForClient(communication)
    thread.join()
    

if __name__ == "__main__":
    main()