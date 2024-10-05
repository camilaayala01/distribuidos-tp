from .common.sorterConsolidatorIndieTop import SorterConsolidatorIndieTop

# should get from env
TOP_AMOUNT = 5

def main():
    sorter = SorterConsolidatorIndieTop(TOP_AMOUNT)
    sorter.execute()

if __name__ == "__main__":
    main()