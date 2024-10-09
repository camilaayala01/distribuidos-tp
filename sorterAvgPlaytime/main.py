import os
from common.sorterAvgPlaytime import SorterAvgPlaytime
import signal

def main():
    sorter = SorterAvgPlaytime(int(os.getenv('TOP_AMOUNT')))
    signal.signal(signal.SIGTERM, sorter.stop)
    sorter.execute()

if __name__ == "__main__":
    main()