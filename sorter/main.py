from common.sorter import Sorter
import signal

def main():
    sorter = Sorter()
    signal.signal(signal.SIGTERM, sorter.stop)
    sorter.execute()

if __name__ == "__main__":
    main()