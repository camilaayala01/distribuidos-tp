from threading import Thread
from common.borderNode import BorderNode
import signal

def main():
    border = BorderNode()
    signal.signal(signal.SIGTERM, border.stop)
    thread = Thread(target=border.listenForClient, args=())
    thread.start()
    border.dispatchResponses()
    thread.join()
    

if __name__ == "__main__":
    main()