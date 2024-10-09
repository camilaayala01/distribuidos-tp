from threading import Thread
from common.borderCommunication import BorderNodeCommunication
import signal

def listenForClient(communication: BorderNodeCommunication):
    while communication.isRunning():
        msg = communication.receiveFromClient()
        if msg == None:
            continue
        communication.sendInitializer(msg)
    communication.closeClientSocket()

def main():
    communication = BorderNodeCommunication()
    signal.signal(signal.SIGTERM, communication.stop)
    thread = Thread(target=listenForClient, args=(communication,))
    thread.start()
    communication.execute()
    thread.join()
    

if __name__ == "__main__":
    main()