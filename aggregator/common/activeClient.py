from entryParsing.common.header import HeaderInterface
from packetTracker.tracker import TrackerInterface

class ActiveClient:
    def __init__(self, initialResults, tracker: TrackerInterface):
        self._fragment = 1
        self._tracker = tracker
        self._sent = set()
        self._partialRes = initialResults

    def isDone(self):
        return self._tracker.isDone()
    
    def update(self, header: HeaderInterface):
        self._tracker.update(header)
    
    def isDuplicate(self, header: HeaderInterface) -> bool:
        return self._tracker.isDuplicate(header)