from common.joinerStreamConsolidator import JoinerStreamConsolidator
import signal

def main():
    joiner = JoinerStreamConsolidator()
    signal.signal(signal.SIGTERM, joiner.stop)
    joiner.execute()

if __name__ == "__main__":
    main()