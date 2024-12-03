import csv
import os
from uuid import UUID

from entryParsing.headerInterface import HeaderInterface
from entryParsing.messagePart import MessagePartInterface

class ActiveClient:
    def __init__(self, clientId: UUID, fragment=None, tracker=None):
        self._clientId = clientId
        self._fragment = fragment
        self._tracker = tracker
        os.makedirs(self.getFolderPath(), exist_ok=True)
    
    def getClientIdBytes(self):
        return self._clientId.bytes

    def destroy(self):
        if os.path.exists(self.storagePath() + '.csv'):
            os.remove(self.storagePath() + '.csv')
    
    def finishedReceiving(self):
        return self._tracker.isDone()

    def getFolderPath(self):
        return f"/{os.getenv('LISTENING_QUEUE')}/clientData/"
    
    def storagePath(self):
        return self.getFolderPath() + f'{self._clientId}'
    
    def storeTracker(self, file) -> int:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(self._tracker.asCSVRow())
        
    def storeEntry(self, entry: MessagePartInterface, file):        
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)    
        written = writer.writerow(entry.__dict__.values())
        if written < entry.expectedCsvLen():
            raise Exception('File could not be written properly')
    
    def loadFragmentFromPath(self, filepath):
        if not os.path.exists(filepath):
            return
        with open(filepath, 'rb') as file:
            file.seek(-2, os.SEEK_END)
            while file.read(1) != b'\n':
                file.seek(-2, os.SEEK_CUR)
            lastLine = file.readline().decode().strip()
        self._fragment = int(lastLine)


    def loadEntries(self, entryType, filepath):
        if not os.path.exists(filepath):
            return iter([])
        
        with open(filepath, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
            next(reader) # skip packet tracker
            for row in reader:
                if self._fragment is not None:
                    try:
                        yield entryType.fromArgs(row), False
                    except TypeError:
                        # reached end of entries, got to fragment number
                        yield int(row[0]), True
                else:
                    yield entryType.fromArgs(row)

    def update(self, header: HeaderInterface):
        self._tracker.update(header)
    
    def isDuplicate(self, header: HeaderInterface) -> bool:
        return self._tracker.isDuplicate(header)
    
    def saveNewResults(self):
        os.rename(self.storagePath() + '.tmp', self.storagePath() + '.csv')
    
