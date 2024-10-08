import signal
from common.joinerIndiePositive import JoinerIndiePositiveReviews

def main():
    joiner = JoinerIndiePositiveReviews()
    signal.signal(signal.SIGTERM, joiner.stop)
    joiner.execute()

if __name__ == "__main__":
    main()