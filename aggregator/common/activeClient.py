import os
from entryParsing.common.header import HeaderInterface
from packetTracker.tracker import TrackerInterface

class ActiveClient:
    def __init__(self, clientId, initialResults, tracker: TrackerInterface):
        self._clientId = clientId
        self._fragment = 1 # persistir :(
        self._tracker = tracker
        self._partialRes = initialResults
        self._folderPath = f"/{os.getenv('LISTENING_QUEUE')}/clientData/"
        os.makedirs(self._folderPath, exist_ok=True)

    def getClientIdBytes(self):
        return self._clientId.bytes
        
    def isDone(self):
        return self._tracker.isDone()
    
    def destroy(self):
        if os.path.exists(self.partialResPath() + '.csv'):
            os.remove(self.partialResPath() + '.csv')

    def partialResPath(self):
        return self._folderPath + f'{self._clientId}'

    def update(self, header: HeaderInterface):
        self._tracker.update(header)
    
    def isDuplicate(self, header: HeaderInterface) -> bool:
        return self._tracker.isDuplicate(header)