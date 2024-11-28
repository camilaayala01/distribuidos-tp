import csv
import os
import shutil
from uuid import UUID
from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface
from packetTracker.packetTracker import PacketTracker

class ActiveClient:
    def __init__(self, clientId: UUID, entryType: type, sorterType: type):
        self._clientId = clientId
        self._entryType = entryType
        self._savedEntries = 0
        self._writtenInTmp = 0
        self._folderPath = f"/{os.getenv('LISTENING_QUEUE')}/clientData/"
        os.makedirs(self._folderPath, exist_ok=True)
        self._tracker = sorterType.initializeTracker(self._folderPath + f'{self._clientId}.csv')

    def destroy(self):
        if os.path.exists(self._folderPath + f'{self._clientId}.csv'):
            os.remove(self._folderPath + f'{self._clientId}.csv')
    
    def getClientIdBytes(self):
        return self._clientId.bytes

    def getResults(self) -> tuple[any, int]:
        return self.loadEntries(), self._savedEntries
    
    def isDone(self):
        return self._tracker.isDone()
    
    def update(self, header: Header):
        self._tracker.update(header)
    
    def isDuplicate(self, header: Header) -> bool:
        return self._tracker.isDuplicate(header)

    def storeEntry(self, entry: EntryInterface):
        filepath = self._folderPath + f'{self._clientId}.tmp'
        with open(filepath, 'a+') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
            if self._writtenInTmp == 0:
                writer.writerow(self._tracker.asRows())
            writer.writerow(entry.__dict__.values())
            self._writtenInTmp += 1
    
    def loadEntries(self):
        filepath = self._folderPath + f'{self._clientId}.csv'
        if not os.path.exists(filepath):
            return iter([])
        
        with open(filepath, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
            next(reader) #skip packer tracker CUANTOS?
            for row in reader:
                yield self._entryType.fromArgs(row)
    

    def newSavedAmount(self, savedAmount: int): #queda en memoria
        self._savedEntries = savedAmount

    def saveNewTop(self):
        path = self._folderPath + f'{self._clientId}'
        os.rename(path + '.tmp', path + '.csv')
        self._writtenInTmp = 0
    