import csv
import os
from uuid import UUID
from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface

class ActiveClient:
    def __init__(self, clientId: UUID, entryType: type, tracker):
        self._clientId = clientId
        self._entryType = entryType
        self._savedEntries = 0
        self._writtenInTmp = 0
        self._folderPath = f"/{os.getenv('LISTENING_QUEUE')}/clientData/"
        os.makedirs(self._folderPath, exist_ok=True)
        self._tracker = tracker
        self._file = None

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

    def openFile(self):
        if self._file is not None:
            return
        filepath = self._folderPath + f'{self._clientId}.tmp'
        self._file = open(filepath, 'w+')

    def closeFile(self):
        if self._file is None:
            return
        self._file.close()

    def storeEntry(self, entry: EntryInterface):
        if self._file is None:
            raise Exception("Cannot write to a closed file")
        
        writer = csv.writer(self._file, quoting=csv.QUOTE_MINIMAL)
        if self._writtenInTmp == 0:
            writer.writerow(self._tracker.asCSVRow())
        writer.writerow(entry.__dict__.values())
        self._writtenInTmp += 1
    
    def loadEntries(self):
        filepath = self._folderPath + f'{self._clientId}.csv'
        if not os.path.exists(filepath):
            return iter([])
        
        with open(filepath, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
            next(reader) # skip packet tracker 
            for row in reader:
                yield self._entryType.fromArgs(row)
    
    def newSavedAmount(self, savedAmount: int): #queda en memoria
        self._savedEntries = savedAmount

    def saveNewTop(self):
        path = self._folderPath + f'{self._clientId}'
        os.rename(path + '.tmp', path + '.csv')
        self._writtenInTmp = 0
    