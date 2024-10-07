import os
from common.sorterConsolidatorIndieTop import SorterConsolidatorIndieTop

def main():
    sorter = SorterConsolidatorIndieTop(int(os.getenv('TOP_AMOUNT')))
    sorter.execute()

if __name__ == "__main__":
    main()