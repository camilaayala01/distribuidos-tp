from common.filtererIndie import FiltererIndie
import signal

def main():
    filterer = FiltererIndie()
    signal.signal(signal.SIGTERM, filterer.stop)
    filterer.execute()

if __name__ == "__main__":
    main()