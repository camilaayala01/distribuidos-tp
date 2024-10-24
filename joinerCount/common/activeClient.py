from entryParsing.common.header import Header
from packetTracker.defaultTracker import DefaultTracker

class ActiveClient:
    def __init__(self, initialResults):
        self._fragment = 1
        self._tracker = DefaultTracker()
        self._sent = set()
        self._counts = initialResults

    def isDone(self):
        return self._tracker.isDone()
    
    def update(self, header: Header):
        self._tracker.update(header)
    
    def isDuplicate(self, header: Header) -> bool:
        return self._tracker.isDuplicate(header)