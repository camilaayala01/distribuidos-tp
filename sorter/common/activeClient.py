import csv
import os
from uuid import UUID
from entryParsing.headerInterface import HeaderInterface
from entryParsing.messagePart import MessagePartInterface

class ActiveClient:
    def __init__(self, clientId: UUID, entryType: type, tracker):
        self._clientId = clientId
        self._entryType = entryType
        self._folderPath = f"/{os.getenv('LISTENING_QUEUE')}/clientData/"
        os.makedirs(self._folderPath, exist_ok=True)
        self._tracker = tracker

    def storagePath(self):
        return self._folderPath + f'{self._clientId}'

    def destroy(self):
        if os.path.exists(self.storagePath() + '.csv'):
            os.remove(self.storagePath() + '.csv')
    
    def getClientIdBytes(self):
        return self._clientId.bytes

    def getResults(self):
        return self.loadEntries()
    
    def isDone(self):
        return self._tracker.isDone()
    
    def update(self, header: HeaderInterface):
        self._tracker.update(header)
    
    def isDuplicate(self, header: HeaderInterface) -> bool:
        return self._tracker.isDuplicate(header)

    def storeTracker(self, file) -> int:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(self._tracker.asCSVRow())
        
    def storeEntry(self, entry: MessagePartInterface, file):            
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(entry.__dict__.values())
    
    def loadEntries(self):
        filepath = self.storagePath() + '.csv'
        if not os.path.exists(filepath):
            return iter([])
        
        with open(filepath, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
            next(reader) # skip packet tracker 
            for row in reader:
                yield self._entryType.fromArgs(row)

    def saveNewTop(self):
        os.rename(self.storagePath() + '.tmp', self.storagePath() + '.csv')
    