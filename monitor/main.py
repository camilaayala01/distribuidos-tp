import signal
from monitor import Monitor
import os

TIMER_DURATION = int(os.getenv('TIMER_DURATION'))

def main():
    monitor = Monitor()
    signal.signal(signal.SIGTERM, monitor.stop)
    signal.signal(signal.SIGALRM, monitor.checkStatus)
    signal.setitimer(signal.ITIMER_REAL, TIMER_DURATION, TIMER_DURATION)
    monitor.run()
    
if __name__ == "__main__":
    main()