from common.sorterConsolidatorAvgPlaytime import SorterConsolidatorAvgPlaytime

# should get from env file
TOP_AMOUNT = 10

def main():
    sorter = SorterConsolidatorAvgPlaytime(TOP_AMOUNT)
    sorter.execute()

if __name__ == "__main__":
    main()