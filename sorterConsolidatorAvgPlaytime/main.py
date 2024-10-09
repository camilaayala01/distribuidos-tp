import os
from common.sorterConsolidatorAvgPlaytime import SorterConsolidatorAvgPlaytime
import signal 

def main():
    sorter = SorterConsolidatorAvgPlaytime(int(os.getenv('TOP_AMOUNT')))
    signal.signal(signal.SIGTERM, sorter.stop)
    sorter.execute()

if __name__ == "__main__":
    main()