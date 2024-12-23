import logging
import re
import os
import subprocess
from threading import Thread, Lock
from election.election import ElectionHandler
from entryParsing.common.utils import initializeLog
from healthcheckAnswerController.messages import HeartbeatMessage
from utils import container, getSocket, monitorName, sendall
from status import Status

TIMER_DURATION = int(os.getenv('TIMER_DURATION'))
HEALTHCHECK_PORT = int(os.getenv('HEALTHCHECK_PORT'))

class Monitor:
    def __init__(self):
        initializeLog()
        self._running = True
        self._id = int(os.getenv('ID'))
        self._electionHandler = ElectionHandler()
        nodesToCheck = set(re.split(r';', os.getenv('TO_CHECK')) if os.getenv('TO_CHECK') else [])
        monitorsToCheck = set([id for id in range(1, int(os.getenv('MONITOR_COUNT')) + 1) if id != self._id])
        self._toCheck = set(map(lambda m: monitorName(m), monitorsToCheck)).union(nodesToCheck)
        self._pendingLock = Lock()
        self._pending = {}
      
    def isRunning(self):
        return self._running
    
    def stop(self, _signum, _frame):
        self._running = False
        self._electionHandler.stop()
    
    def revive(self, node):
        logging.info(f"action: reviving node {node}")
        result = subprocess.run(['docker', 'start', container(node)], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info('action: command executed. Result={}. Output={}. Error={}'.format(result.returncode, result.stdout, result.stderr))

    def checkLeader(self):
        if not self._electionHandler.isLeaderRunning():
            return
        leader = monitorName(self._electionHandler.getLeader())
        with self._pendingLock:
            if leader not in self._pending:
                self.setPendingStatus(False)
            status = self._pending[leader]
            if status.expired():
                with self._electionHandler.getLeaderIsRunningLock():
                    self._electionHandler.startElection()
            self._pending[leader].update()

    def checkForDeadNodes(self):
        deadNodes = []
        with self._pendingLock:
            for node in self._pending:
                if self._pending[node].expired():
                    deadNodes.append(node)
        for node in deadNodes:
            self.revive(node)
            with self._pendingLock:
                self._pending[node].reset()

    def checkStatus(self, _signum, _frame):
        if not self._electionHandler.isLeaderRunning() or not self.isRunning():
            return
        match self._electionHandler.iAmLeader():
            case True:
                self.checkForDeadNodes()
                self.sendHealthcheck()
            case False:
                self.checkLeader()
    
    def sendHealthcheck(self):
        sock = self._healthcheckSock
        for id in self._toCheck:
            if not self._electionHandler.iAmLeader():
                break
            sendall(HeartbeatMessage.CHECK.serialize(monitorName(self._id)), (id, HEALTHCHECK_PORT), sock)   
            with self._pendingLock:
                self._pending[id].update()

    def listenForHealthcheckAnswer(self):
        sock = self._healthcheckSock
        while self.isRunning() and self._electionHandler.iAmLeader():
            try:
                data, _ = sock.recvfrom(1024)
                msg, node  = HeartbeatMessage.deserialize(data)
                if msg == HeartbeatMessage.ACK:
                    with self._pendingLock:
                        self._pending[node].reset()
            except TimeoutError:
                continue
        sock.close()

    def listenForLeader(self):
        sock = self._healthcheckSock
        while self.isRunning() and self._electionHandler.isLeaderRunning(): 
            try:
                data, addr = sock.recvfrom(1024)
                msg, node = HeartbeatMessage.deserialize(data)    
                if msg == HeartbeatMessage.CHECK:
                    with self._pendingLock:
                        if monitorName(self._electionHandler.getLeader()) not in self._pending:
                            self.setPendingStatus(False)
                        self._pending[monitorName(self._electionHandler.getLeader())].reset()
                    sendall(HeartbeatMessage.ACK.serialize(monitorName(self._id)), addr, sock)
            except TimeoutError:
                continue

        if not self.isRunning():
            return

        sock.close()
        self._electionHandler.waitForNewLeader()

    def setPendingStatus(self, isLeader):
        self._pending = {}
        match isLeader:
            case True:
                for node in self._toCheck:
                    self._pending[node] = Status()         
            case False:
                self._pending.setdefault(monitorName(self._electionHandler.getLeader()), Status())

    def runMonitor(self): 
        with self._pendingLock:
            self.setPendingStatus(self._electionHandler.iAmLeader())
        self._healthcheckSock = getSocket(self._id, HEALTHCHECK_PORT, TIMER_DURATION)
        self._electionHandler.setLeaderIsRunning(True)
        match self._electionHandler.iAmLeader():
            case True:
                self._electionHandler.sendCoordinator()
                logging.info("action: starting execution as leader monitor | success")
                self.listenForHealthcheckAnswer()
            case False:
                logging.info("action: starting execution as not leader monitor | success")
                self.listenForLeader()

    def run(self):
        electionThread = Thread(target=self._electionHandler.listenForElection)
        electionThread.start()
        while self.isRunning():
            self.runMonitor()
        electionThread.join()