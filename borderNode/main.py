from threading import Thread, Event
from common.borderCommunication import BorderNodeCommunication
from common.clientAccepter import ClientAccepter
import signal
from common.responseDispatcher import ResponseDispatcher


def main():
    stopEvent = Event()
    borderCommunication = BorderNodeCommunication()
    accepter = ClientAccepter(borderCommunication, stopEvent)
    dispatcher = ResponseDispatcher(borderCommunication, stopEvent)
    signal.signal(signal.SIGTERM, dispatcher.stop)
    signal.signal(signal.SIGALRM, accepter.handleTimeoutSignal)
    signal.setitimer(signal.ITIMER_REAL, 2, 2)
    thread = Thread(target=accepter.listenForClient, args=())
    thread.start()
    dispatcher.execute()
    thread.join()
    
if __name__ == "__main__":
    main()