import signal
from common.joinerOSCount import JoinerOSCount
from entryParsing.common.utils import initializeLog

def main():
    initializeLog()
    joiner = JoinerOSCount()
    signal.signal(signal.SIGTERM, joiner.stop)
    joiner.execute()

if __name__ == "__main__":
    main()