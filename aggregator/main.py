import signal
from entryParsing.common.utils import initializeLog
from common.aggregator import Aggregator

def main():
    initializeLog()
    joiner = Aggregator()
    signal.signal(signal.SIGTERM, joiner.stop)
    joiner.execute()

if __name__ == "__main__":
    main()