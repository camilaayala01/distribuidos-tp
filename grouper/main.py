from common.grouper import Grouper
import signal

def main():
    grouper = Grouper()
    signal.signal(signal.SIGTERM, grouper.stop)
    grouper.execute()

if __name__ == "__main__":
    main()