from common.filterer import Filterer
import signal

def main():
    filterer = Filterer()
    signal.signal(signal.SIGTERM, filterer.stop)
    filterer.execute()

if __name__ == "__main__":
    main()