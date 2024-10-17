import signal
from entryParsing.common.utils import initializeLog
from common.joinerCount import JoinerCount

def main():
    initializeLog()
    joiner = JoinerCount()
    signal.signal(signal.SIGTERM, joiner.stop)
    joiner.execute()

if __name__ == "__main__":
    main()