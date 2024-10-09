from common.joinerEnglishCount import JoinerNegativeReviewsEnglishCount
import signal

def main():
    joiner = JoinerNegativeReviewsEnglishCount()
    signal.signal(signal.SIGTERM, joiner.stop)
    joiner.execute()

if __name__ == "__main__":
    main()