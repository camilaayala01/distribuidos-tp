import os
from common.sorterConsolidatorIndieTop import SorterConsolidatorIndieTop
import signal

def main():
    sorter = SorterConsolidatorIndieTop(int(os.getenv('TOP_AMOUNT')))
    signal.signal(signal.SIGTERM, sorter.stop)
    sorter.execute()

if __name__ == "__main__":
    main()