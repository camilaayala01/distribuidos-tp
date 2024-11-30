import csv
import os
from uuid import UUID
from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface

class ActiveClient:
    def __init__(self, clientId: UUID, entryType: type, tracker):
        self._clientId = clientId
        self._entryType = entryType
        self._folderPath = f"/{os.getenv('LISTENING_QUEUE')}/clientData/"
        os.makedirs(self._folderPath, exist_ok=True)
        self._tracker = tracker

    def destroy(self):
        if os.path.exists(self._folderPath + f'{self._clientId}.csv'):
            os.remove(self._folderPath + f'{self._clientId}.csv')
    
    def getClientIdBytes(self):
        return self._clientId.bytes

    def getResults(self):
        return self.loadEntries()
    
    def isDone(self):
        return self._tracker.isDone()
    
    def update(self, header: Header):
        self._tracker.update(header)
    
    def isDuplicate(self, header: Header) -> bool:
        return self._tracker.isDuplicate(header)

    def getTmpPath(self):
        return self._folderPath + f'{self._clientId}.tmp'

    def storeTracker(self, file):
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(self._tracker.asCSVRow())
        
    def storeEntry(self, entry: EntryInterface, file):            
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(entry.__dict__.values())
    
    def loadEntries(self):
        filepath = self._folderPath + f'{self._clientId}.csv'
        if not os.path.exists(filepath):
            return iter([])
        
        with open(filepath, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
            next(reader) # skip packet tracker 
            for row in reader:
                yield self._entryType.fromArgs(row)

    def saveNewTop(self):
        path = self._folderPath + f'{self._clientId}'
        os.rename(path + '.tmp', path + '.csv')
    