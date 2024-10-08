import os
from common.sorterConsolidatorAvgPlaytime import SorterConsolidatorAvgPlaytime

def main():
    sorter = SorterConsolidatorAvgPlaytime(int(os.getenv('TOP_AMOUNT')))
    sorter.execute()

if __name__ == "__main__":
    main()