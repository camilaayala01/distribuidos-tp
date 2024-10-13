from common.joiner import Joiner
import signal

def main():
    joiner = Joiner()
    signal.signal(signal.SIGTERM, joiner.stop)
    joiner.execute()

if __name__ == "__main__":
    main()