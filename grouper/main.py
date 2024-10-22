import logging
from common.grouper import Grouper
import signal

def main():
    try:
        grouper = Grouper()
        signal.signal(signal.SIGTERM, grouper.stop)
        grouper.execute()
    except Exception as e:
        logging.error(e)

if __name__ == "__main__":
    main()