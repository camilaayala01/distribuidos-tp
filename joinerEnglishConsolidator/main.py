from common.joinerEnglishConsolidator import JoinerEnglishConsolidator
import signal

def main():
    joiner = JoinerEnglishConsolidator()
    signal.signal(signal.SIGTERM, joiner.stop)
    joiner.execute()

if __name__ == "__main__":
    main()