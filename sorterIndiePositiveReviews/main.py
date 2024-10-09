import os
from common.sorterIndiePositiveReviews import SorterIndiePositiveReviews
import signal 

def main():
    sorter = SorterIndiePositiveReviews(int(os.getenv('TOP_AMOUNT')))
    signal.signal(signal.SIGTERM, sorter.stop)
    sorter.execute()

if __name__ == "__main__":
    main()