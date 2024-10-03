from entryParsing.common.headerWithSender import HeaderWithSender
from packetTracker.defaultTracker import DefaultTracker

class MultiTracker:
    def __init__(self, priorNodeCount: int):
        self._trackers = [DefaultTracker() for _ in range(priorNodeCount)]

    def getProcessingTracker(self, header: HeaderWithSender):
        return self._trackers[header.getSenderID() - 1]
    
    def isDuplicate(self, header: HeaderWithSender):
        return self.getProcessingTracker(header).isDuplicate(header)

    def update(self, header: HeaderWithSender):
        self.getProcessingTracker(header).update(header)
    
    def isDone(self) -> bool:
        for tracker in self._trackers:
            if not tracker.isDone():
                return False
        
        return True
    
    def reset(self):
        for tracker in self._trackers:
            tracker.reset()