from common.filtererAction import FiltererAction
import signal

def main():
    filterer = FiltererAction()
    signal.signal(signal.SIGTERM, filterer.stop)
    filterer.execute()

if __name__ == "__main__":
    main()