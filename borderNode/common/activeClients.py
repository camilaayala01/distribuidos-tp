import os
import threading
import time
from uuid import UUID
from entryParsing.common.fieldParsing import getClientIdUUID
from entryParsing.common.utils import copyFile

UUID_LEN = 36

class ActiveClients:
    def __init__(self):
        folderPath = os.getenv('STORAGE_PATH')
        os.makedirs(folderPath, exist_ok=True)
        self._storagePath = folderPath + 'activeClients'
        # key=clientID bytes, value=time of the last message client sent
        self._clientMonitor = self.loadState()
        self._clientsMonitorLock = threading.Lock()
        self._clientsFileLock = threading.Lock()
        
    def loadState(self):
        clients = {}
        file_path = self._storagePath + self.storageFileExtension()

        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                buffer = ""
                while chunk := file.read(1024):
                    buffer += chunk
                    while len(buffer) >= UUID_LEN:
                        uuid_str = buffer[:UUID_LEN]
                        buffer = buffer[UUID_LEN:]
                        try:
                            print("loading client", uuid_str)
                            clients[UUID(uuid_str).bytes] = time.perf_counter()
                        except ValueError as e:
                            raise Exception(f"Error in clients file: file is corrupted")
        return clients
    
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
        
        for client in clientsToRemove:
            with self._clientsMonitorLock:
                if client in self._clientMonitor:
                    self._clientMonitor.pop(client)
                    removed.add(getClientIdUUID(client))
        # monitor is consistent to file. when there is a failure, at reboot 
        # monitor will take its information from file
        self.removeClientsFromFile(removed)

    def removeClientsFromFile(self, clientsToRemove: set[UUID]):
        if not clientsToRemove:
            return
        sourcePath = self._storagePath + self.storageFileExtension()
        tempPath =  self._storagePath + '.tmp'
        buffer = ""
        with self._clientsFileLock:
            with open(sourcePath, 'r') as source, open(tempPath, 'w') as destination:
                while chunk := source.read(1024):
                    buffer += chunk
                    while len(buffer) >= UUID_LEN:
                        uuid_str = buffer[:UUID_LEN]
                        buffer = buffer[UUID_LEN:]
                        if UUID(uuid_str) not in clientsToRemove:
                            destination.write(f"{uuid_str}")
            os.rename(tempPath, sourcePath)

    def setTimestampForClient(self, clientId: bytes):
        with self._clientsMonitorLock:
            self._clientMonitor[clientId] = time.perf_counter()

    def storeNewClient(self, clientId: bytes):
        self.setTimestampForClient(clientId)
        with self._clientsFileLock:
            self.storeInDisk(getClientIdUUID(clientId))
    
    def storeInDisk(self, clientId: UUID):
        storageFilePath = self._storagePath
        with open(storageFilePath + '.tmp', 'w') as newResults:
            copyFile(newResults, storageFilePath + self.storageFileExtension())
            newResults.write(f"{clientId}")
        os.rename(storageFilePath + '.tmp', storageFilePath + self.storageFileExtension())

    def getExpiredTimers(self, lastTimer: float) -> tuple[float, set[bytes]]:
        now = time.perf_counter()
        with self._clientsMonitorLock:
            expired = {clientId for clientId, clientTimer in self._clientMonitor.items() if lastTimer > clientTimer}
        return now, expired