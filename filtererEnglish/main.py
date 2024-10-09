from common.filtererEnglish import FiltererEnglish
import signal

def main():
    filterer = FiltererEnglish()
    signal.signal(signal.SIGTERM, filterer.stop)
    filterer.execute()

if __name__ == "__main__":
    main()