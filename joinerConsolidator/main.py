from common.joinerConsolidator import JoinerConsolidator
import signal

def main():
    joinerConsolidator = JoinerConsolidator()
    signal.signal(signal.SIGTERM, joinerConsolidator.stop)
    joinerConsolidator.execute()

if __name__ == "__main__":
    main()