from .common.sorterIndiePositiveReviews import SorterIndiePositiveReviews

# should get from env
TOP_AMOUNT = 5

def main():
    sorter = SorterIndiePositiveReviews(TOP_AMOUNT)
    sorter.execute()

if __name__ == "__main__":
    main()