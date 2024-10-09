from common.joinerActionEnglish import JoinerActionNegativeReviewsEnglish
import signal

def main():
    joiner = JoinerActionNegativeReviewsEnglish()
    signal.signal(signal.SIGTERM, joiner.stop)
    joiner.execute()

if __name__ == "__main__":
    main()