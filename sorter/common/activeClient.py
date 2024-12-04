
from uuid import UUID
from statefulNode.activeClient import ActiveClient

class SorterClient(ActiveClient):
    def __init__(self, clientId: UUID, entryType: type, tracker):
        super().__init__(clientId=clientId, tracker=tracker)
        self._entryType = entryType

    def getResults(self):
        return self.loadEntries()
    
    def loadEntries(self):
        return super().loadEntries(self._entryType, self.storagePath() + '.csv')
    
    