import os
from common.sorterAvgPlaytime import SorterAvgPlaytime

def main():
    sorter = SorterAvgPlaytime(int(os.getenv('TOP_AMOUNT')))
    sorter.execute()

if __name__ == "__main__":
    main()