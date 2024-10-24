from entryParsing.common.header import Header
from packetTracker.multiTracker import MultiTracker

class ActiveClient:
    def __init__(self, priorNodeCount):
        self._fragment = 1
        self._tracker = MultiTracker(priorNodeCount)
    
    def isDone(self):
        return self._tracker.isDone()
    
    def update(self, header: Header):
        self._tracker.update(header)
    
    def isDuplicate(self, header: Header) -> bool:
        return self._tracker.isDuplicate(header)