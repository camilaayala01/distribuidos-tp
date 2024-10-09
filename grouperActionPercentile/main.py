from common.grouperActionPercentile import GrouperActionPercentileNegativeReviews
import signal 

def main():
    grouper = GrouperActionPercentileNegativeReviews()
    signal.signal(signal.SIGTERM, grouper.stop)
    grouper.execute()

if __name__ == "__main__":
    main()