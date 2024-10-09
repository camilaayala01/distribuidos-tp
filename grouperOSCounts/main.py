from common.grouperOSCounts import GrouperOSCounts
import signal 

def main():
    grouper = GrouperOSCounts()
    signal.signal(signal.SIGTERM, grouper.stop)
    grouper.execute()

if __name__ == "__main__":
    main()