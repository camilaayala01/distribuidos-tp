
from uuid import UUID
from statefulNode.activeClient import ActiveClient

class SorterClient(ActiveClient):
    def __init__(self, clientId: UUID, entryType: type, tracker):
        super().__init__(clientId, tracker)
        self._entryType = entryType

    def getResults(self):
        return self.loadEntries()
    
   
    
    