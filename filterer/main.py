import logging
from common.filterer import Filterer
import signal

def main():
    try:
        filterer = Filterer()
        signal.signal(signal.SIGTERM, filterer.stop)
        filterer.execute()
    except Exception as e:
        logging.error(e)
    

if __name__ == "__main__":
    main()