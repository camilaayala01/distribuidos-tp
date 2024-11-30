import os
import csv
from entryParsing.common.header import HeaderInterface
from packetTracker.tracker import TrackerInterface

class ActiveClient:
    def __init__(self, clientId, initialResults, tracker: TrackerInterface):
        self._clientId = clientId
        self._fragment = 1 # TODO persistir :(
        self._tracker = tracker
        self._partialRes = initialResults
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
        return writer.writerow(self._tracker.asCSVRow())

    def storagePath(self):
        return self._folderPath + f'{self._clientId}'

    def loadEntries(self, entryType):
        filepath = self.storagePath() + '.csv'
        if not os.path.exists(filepath):
            return iter([])
        
        with open(self.storagePath() + '.csv', 'r+') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
            next(reader) # skip packet tracker
            for row in reader:
                try:
                    yield entryType.fromArgs(row)
                except Exception as e:
                    print("exception", e)
                    print(row)

    def update(self, header: HeaderInterface):
        self._tracker.update(header)
    
    def isDuplicate(self, header: HeaderInterface) -> bool:
        return self._tracker.isDuplicate(header)
    
    def saveNewResults(self):
        os.rename(self.storagePath() + '.tmp', self.storagePath() + '.csv')

    