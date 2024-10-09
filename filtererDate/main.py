from common.filtererDate import FiltererDate
import signal

def main():
    filterer = FiltererDate()
    signal.signal(signal.SIGTERM, filterer.stop)
    filterer.execute()

if __name__ == "__main__":
    main()