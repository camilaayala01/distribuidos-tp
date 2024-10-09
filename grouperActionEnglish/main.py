from common.grouperActionEnglish import GrouperActionEnglishNegativeReviews
import signal 

def main():
    grouper = GrouperActionEnglishNegativeReviews()
    signal.signal(signal.SIGTERM, grouper.stop)
    grouper.execute()

if __name__ == "__main__":
    main()