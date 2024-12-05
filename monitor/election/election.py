import logging
import os
from threading import Lock, Semaphore
from .messages import ElectionMessage
from utils import getServerSocket, sendto

PORT = int(os.getenv('ELECTION_PORT'))
MONITOR_COUNT = int(os.getenv('MONITOR_COUNT'))
TIMEOUT = int(os.getenv('TIMER_DURATION'))

class ElectionHandler:
    def __init__(self):
        self._running = True
        self._id = int(os.getenv('ID'))
        self._leader = MONITOR_COUNT
        self._leaderIsRunning = True
        self._leaderSemaphore = Semaphore(0)
        self._leaderIsRunningLock = Lock()

    def stop(self):
        self._running = False
        self._leaderIsRunning = False 
        self._leaderSemaphore.release()
        
    def setLeaderIsRunning(self, running):
        with self._leaderIsRunningLock:
            self._leaderIsRunning = running

    def isRunning(self):
        return self._running
    
    def isLeaderRunning(self):
        return self._leaderIsRunning

    def getLeaderIsRunningLock(self):
        return self._leaderIsRunningLock
    
    def getLeader(self):
        return self._leader
    
    def iAmLeader(self) -> bool:
        return self._id == self._leader
    
    def waitForNewLeader(self): 
        try:
            self._leaderSemaphore.acquire(timeout=TIMEOUT)
        except TimeoutError:
            self.startElection()

    def resolveElection(self):
        self._leaderSemaphore.release()

    def sendCoordinator(self): 
        for id in range(1, self._leader):
            s = sendto(senderId=self._id, port=PORT, recvId=id, msg=ElectionMessage.COORDINATOR, timeout=TIMEOUT)
            if s is not None:
                s.close()

    def declareAsLeader(self):
        self._leader = self._id
        self.resolveElection()
    
    def listenForElection(self): 
        listeningSock = getServerSocket(self._id, PORT, TIMEOUT)
        while self.isRunning():
            try:
                (sock, _addr) = listeningSock.accept()
                data = sock.recv(ElectionMessage.size())
                msg, sender = ElectionMessage.deserialize(data)
                match msg:
                    case ElectionMessage.ELECTION:
                        sock.sendall(ElectionMessage.ANSWER.serialize(self._id))
                        with self.getLeaderIsRunningLock(): 
                            if self.isLeaderRunning():
                                self.startElection()
                    case ElectionMessage.COORDINATOR:
                        self._leader = sender
                        with self.getLeaderIsRunningLock():
                            if not self.isLeaderRunning():
                                self.resolveElection()
                sock.close()
            except TimeoutError:
                continue
        listeningSock.close()
       
    def startElection(self):
        logging.info(f"action: leader down, participarting of an election")
        self._leaderIsRunning = False 
        candidates = 0
        for id in range(self._id + 1, MONITOR_COUNT + 1):
            s = sendto(senderId=self._id, port=PORT, recvId=id, msg=ElectionMessage.ELECTION,timeout=TIMEOUT)
            if s is not None:
                try:
                    data = s.recv(ElectionMessage.size())
                    msg, _sender = ElectionMessage.deserialize(data)
                    if msg == ElectionMessage.ANSWER:
                        candidates += 1
                except TimeoutError:
                    pass
                s.close()
        if candidates == 0:
            self.declareAsLeader()
        