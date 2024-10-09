from common.initializer import Initializer
import signal 

def main():
    initializer = Initializer()
    signal.signal(signal.SIGTERM, initializer.stop)
    initializer.execute()

if __name__ == "__main__":
    main()