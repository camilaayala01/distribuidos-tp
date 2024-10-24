from entryParsing.common.header import Header
from packetTracker.packetTracker import PacketTracker

class ActiveClient:
    def __init__(self, tracker: PacketTracker):
        self._tracker = tracker
        self._partialTop = []

    def isDone(self):
        return self._tracker.isDone()
    
    def update(self, header: Header):
        self._tracker.update(header)
    
    def isDuplicate(self, header: Header) -> bool:
        return self._tracker.isDuplicate(header)