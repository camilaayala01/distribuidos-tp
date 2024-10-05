from .common.sorterAvgPlaytime import SorterAvgPlaytime

# should get from env file
TOP_AMOUNT = 10

def main():
    sorter = SorterAvgPlaytime(TOP_AMOUNT)
    sorter.execute()

if __name__ == "__main__":
    main()