from common.sorterConsolidatorActionPercentile import SorterConsolidatorActionPercentile
import signal

def main():
    sorter = SorterConsolidatorActionPercentile()
    signal.signal(signal.SIGTERM, sorter.stop)
    sorter.execute()

if __name__ == "__main__":
    main()