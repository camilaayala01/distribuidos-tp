from entryParsing.common.headerWithSender import HeaderWithSender
from packetTracker.defaultTracker import DefaultTracker
from packetTracker.tracker import TrackerInterface

class MultiTracker(TrackerInterface):
    def __init__(self, priorNodeCount: int, storagePath: str):
        self._storagePath = storagePath
        self._trackers = {}

    def getProcessingTracker(self, header: HeaderWithSender):
        self._trackers[header.getSenderID()] = self._trackers.get(header.getSenderID(), DefaultTracker(self._storagePath))
        return self._trackers[header.getSenderID()]
    
    def isDuplicate(self, header: HeaderWithSender):
        return self.getProcessingTracker(header).isDuplicate(header)

    def update(self, header: HeaderWithSender):
        self.getProcessingTracker(header).update(header)
    
    def isDone(self) -> bool:
        for tracker in self._trackers.values():
            if tracker.isDone():
                return True
        return False
    
    def reset(self):
        for tracker in self._trackers:
            tracker.reset()