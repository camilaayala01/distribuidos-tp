import os
import threading
import time
from entryParsing.common.utils import copyFile

class ActiveClients:
    def __init__(self):
        folderPath = os.getenv('STORAGE_PATH')
        os.makedirs(folderPath, exist_ok=True)
        self._storagePath = folderPath + 'activeClients'
        self._clientsFileLock = threading.Lock()

        self._clientsMonitorLock = threading.Lock()
        # key=clientID, value=time of the last message client sent
        self._clientMonitor = {}
    
    def isActiveClient(self, clientId):
        with self._clientsMonitorLock:
            return clientId in self._clientMonitor
        
    def storageFileExtension(self):
        return '.txt'
    
    def removeClientFiles(self):
        with self._clientsFileLock:
            datafile = self._storagePath + self.storageFileExtension()
            if os.path.exists(datafile):
                os.remove(datafile)
            tmpfile = self._storagePath + '.tmp'
            if os.path.exists(tmpfile):
                os.remove(tmpfile)

    """ 
    Removes clients from file and monitor if they existed in those.
    Used for when a client hits timeout, or when it finished sending
    data.
    """
    def removeClientsFromActive(self, clientsToRemove: set[bytes]):
        if not clientsToRemove:
            return
        # for when client sends a deletion confirmation; avoid going to disk if everything went well
        removed = set()
        with self._clientsMonitorLock:
            for client in clientsToRemove:
                if client in self._clientMonitor:
                    self._clientMonitor.pop(client)
                    removed.add(client)
        # monitor is consistent to file. when there is a failure, at reboot 
        # monitor will take its information from file
        self.removeClientsFromFile(removed)

    def removeClientsFromFile(self, clientsToRemove: set[bytes]):
        if not clientsToRemove:
            return
        sourcePath = self._storagePath + self.storageFileExtension()
        tempPath =  self._storagePath + '.tmp'
        with self._clientsFileLock:
            with open(sourcePath, 'rb') as source, open(tempPath, 'wb') as destination:
                for line in source:
                    if line not in clientsToRemove:
                        destination.write(line)
            os.rename(tempPath, sourcePath)

    def setTimestampForClient(self, clientId: bytes):
        with self._clientsMonitorLock:
            self._clientMonitor[clientId] = time.perf_counter()

    def storeNewClient(self, clientId: bytes):
        self.setTimestampForClient(clientId)
        with self._clientsFileLock:
            self.storeInDisk(clientId)
    
    def storeInDisk(self, clientId: bytes):
        storageFilePath = self._storagePath
        with open(storageFilePath + '.tmp', 'wb') as newResults:
            copyFile(newResults, storageFilePath + self.storageFileExtension())
            newResults.write(clientId)
        os.rename(storageFilePath + '.tmp', storageFilePath + self.storageFileExtension())

    def getExpiredTimers(self, lastTimer: float) -> tuple[float, set[bytes]]:
        now = time.perf_counter()
        with self._clientsMonitorLock:
            expired = {clientId for clientId, clientTimer in self._clientMonitor.items() if lastTimer > clientTimer}
        return now, expired