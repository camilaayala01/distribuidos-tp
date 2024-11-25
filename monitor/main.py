import signal
from monitor import Monitor


def main():
    monitor = Monitor()
    signal.signal(signal.SIGTERM, monitor.stop)
    signal.signal(signal.SIGALRM, monitor.checkStatus)
    signal.setitimer(signal.ITIMER_REAL, 3, 3)
    monitor.run()
    
if __name__ == "__main__":
    main()