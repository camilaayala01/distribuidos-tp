from common.joinerActionPercentile import JoinerActionNegativeReviewsPercentile
import signal

def main():
    joiner = JoinerActionNegativeReviewsPercentile()
    signal.signal(signal.SIGTERM, joiner.stop)
    joiner.execute()

if __name__ == "__main__":
    main()