from common.joinerIndieConsolidator import JoinerIndiePositiveConsolidator
import signal

def main():
    joiner = JoinerIndiePositiveConsolidator()
    signal.signal(signal.SIGTERM, joiner.stop)
    joiner.execute()

if __name__ == "__main__":
    main()