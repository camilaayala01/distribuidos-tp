from entryParsing.common.headerWithSender import HeaderWithSender
from packetTracker.defaultTracker import DefaultTracker
from packetTracker.tracker import TrackerInterface

class MultiTracker(TrackerInterface):
    def __init__(self, priorNodeCount: int, storagePath: str):
        self._storagePath = storagePath
        self._trackers = {}

    def getProcessingTracker(self, header: HeaderWithSender):
        return self._trackers.get(header.getSenderID(), DefaultTracker(self._storagePath))
    
    def isDuplicate(self, header: HeaderWithSender):
        return self.getProcessingTracker(header).isDuplicate(header)

    def destroy(self):
        # this tracker will cease to exist
        return
    
    def update(self, header: HeaderWithSender):
        self.getProcessingTracker(header).update(header)
    
    def isDone(self) -> bool:
        for tracker in self._trackers:
            if tracker.isDone():
                return True
        return False
    
    def reset(self):
        for tracker in self._trackers:
            tracker.reset()