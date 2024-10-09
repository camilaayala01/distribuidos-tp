from common.grouperIndiePositiveReviews import GrouperIndiePositiveReviews
import signal 

def main():
    grouper = GrouperIndiePositiveReviews()
    signal.signal(signal.SIGTERM, grouper.stop)
    grouper.execute()

if __name__ == "__main__":
    main()