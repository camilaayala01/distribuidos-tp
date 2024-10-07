from threading import Thread
from common.borderCommunication import BorderNodeCommunication

def listenForClient(communication):
    while True:
        msg = communication.receiveFromClient()
        communication.sendInitializer(msg)
        
def main():
    communication = BorderNodeCommunication()
    thread = Thread(target=communication.execute)
    thread.start()
    listenForClient(communication)
    thread.join()
    

if __name__ == "__main__":
    main()