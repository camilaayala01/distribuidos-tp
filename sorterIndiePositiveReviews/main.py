import os
from common.sorterIndiePositiveReviews import SorterIndiePositiveReviews

def main():
    sorter = SorterIndiePositiveReviews(int(os.getenv('TOP_AMOUNT')))
    sorter.execute()

if __name__ == "__main__":
    main()