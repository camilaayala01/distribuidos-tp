import signal
from entryParsing.common.utils import initializeLog
from common.aggregator import Aggregator

def main():
    initializeLog()
    aggregator = Aggregator()
    signal.signal(signal.SIGTERM, aggregator.stop)
    aggregator.execute()

if __name__ == "__main__":
    main()