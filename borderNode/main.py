from threading import Thread
from common.borderCommunication import BorderNodeCommunication

def listenForClient(communication):
    while True:
        msg = communication.receiveFromClient()
        communication.sendInitializer(msg)
        
def main():
    print("corriendo")
    communication = BorderNodeCommunication()
    thread = Thread(target=communication.execute)
    thread.start()
    print("ejecuto el modulo de comunicacion")
    listenForClient(communication)
    thread.join()
    

if __name__ == "__main__":
    main()