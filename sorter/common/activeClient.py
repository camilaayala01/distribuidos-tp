import csv
import os
import shutil
from uuid import UUID
from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface
from packetTracker.packetTracker import PacketTracker

class ActiveClient:
    def __init__(self, tracker: PacketTracker, clientId: UUID, entryType: type):
        self._clientId = clientId
        self._entryType = entryType
        self._tracker = tracker
        self._savedEntries = 0
        self._folderPath = f"/{os.getenv('LISTENING_QUEUE')}/clientData/"
        os.makedirs(self._folderPath, exist_ok=True)

    def destroy(self):
        self._tracker.destroy()
        if os.path.exists(self._folderPath):
            shutil.rmtree(self._folderPath)

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
            writer.writerow(entry.__dict__.values())

    def loadEntries(self):
        filepath = self._folderPath + f'{self._clientId}.csv'
        if not os.path.exists(filepath):
            return iter([])
        
        with open(filepath, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                try:
                    yield self._entryType.fromArgs(row)
                except Exception as e:
                    print("exception", e)
                    print(row)

    def saveNewTop(self, savedAmount: int):
        self._savedEntries = savedAmount
        path = self._folderPath + f'{self._clientId}'
        os.rename(path + '.tmp', path + '.csv')
    