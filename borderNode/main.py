from threading import Thread
from common.borderNode import BorderNode
import signal

def main():
    border = BorderNode()
    print('llegamos acá')
    signal.signal(signal.SIGTERM, border.stop)
    signal.signal(signal.SIGALRM, border.handleTimeoutSignal)
    signal.setitimer(signal.ITIMER_REAL, 2, 2)
    thread = Thread(target=border.listenForClient, args=())
    thread.start()
    border.dispatchResponses()
    thread.join()
    

if __name__ == "__main__":
    main()