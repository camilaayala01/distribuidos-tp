import os
import csv
from uuid import UUID
from entryParsing.common.header import HeaderInterface
from entryParsing.common.utils import nextRow
from packetTracker.tracker import TrackerInterface

class ActiveClient:
    def __init__(self, clientId: UUID, tracker: TrackerInterface):
        self._clientId = clientId
        self._fragment = 1
        self._tracker = tracker
        self._folderPath = f"/{os.getenv('LISTENING_QUEUE')}/clientData/"
        os.makedirs(self._folderPath, exist_ok=True)

    def getClientIdBytes(self):
        return self._clientId.bytes
        
    def finishedReceiving(self):
        return self._tracker.isDone()
    
    def destroy(self):
        if os.path.exists(self.storagePath() + '.csv'):
            os.remove(self.storagePath() + '.csv')

    def storeTracker(self, file) -> int:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(self._tracker.asCSVRow()) 

    # sendingFragments is true if it will be sending data this time
    def storeFragment(self, storageFile, sendingFragments: bool):
        writer = csv.writer(storageFile, quoting=csv.QUOTE_MINIMAL)
        # stores the fragment it will use next time it needs to send data
        writer.writerow([self._fragment + (1 if sendingFragments else 0)])

    def storagePath(self):
        return self._folderPath + f'{self._clientId}'

    def loadFragment(self, filepath):
        with open(filepath, 'rb') as file:
            file.seek(-2, os.SEEK_END)
            while file.read(1) != b'\n':
                file.seek(-2, os.SEEK_CUR)
            lastLine = file.readline().decode().strip()
        self._fragment = int(lastLine)

    def loadEntries(self, entryType):
        filepath = self.storagePath() + '.csv'
        if not os.path.exists(filepath):
            return iter([])
        
        with open(self.storagePath() + '.csv', 'r+') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
            nextRow(reader) # skip packet tracker
            for row in reader:
                try:
                    yield entryType.fromArgs(row), False
                except TypeError:
                    # reached end of entries, got to fragment number
                    yield int(row[0]), True

                
    def update(self, header: HeaderInterface):
        self._tracker.update(header)
    
    def isDuplicate(self, header: HeaderInterface) -> bool:
        return self._tracker.isDuplicate(header)
    
    def saveNewResults(self):
        os.rename(self.storagePath() + '.tmp', self.storagePath() + '.csv')

    