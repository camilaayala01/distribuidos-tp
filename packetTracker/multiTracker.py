from entryParsing.common.headerWithSender import HeaderWithSender
from packetTracker.defaultTracker import DefaultTracker
from packetTracker.tracker import TrackerInterface

class MultiTracker(TrackerInterface):
    def __init__(self):
        # sender: defaultTracker
        self._trackers = {}
    
    def getProcessingTracker(self, header: HeaderWithSender):
        self._trackers[header.getSenderID()] = self._trackers.get(header.getSenderID(), DefaultTracker())
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
    
    def asCSVRow(self):
        row = []
        for senderId, tracker in self._trackers.items():
            row.append(f'{[senderId] + tracker.asCSVRow()}')
        return row
    
    def __repr__(self):
        return " | ".join(f"{key}: {value}" for key, value in self._trackers.items())
    
    #[senderId,biggestFragment,pending,receivedEnd],[senderId,biggestFragment,pending,receivedEnd]
    @classmethod
    def fromStorage(cls, row: list[str]):
        tracker = cls()
        for track in row:
            attrs = eval(track)
            tracker._trackers[attrs[0]] = DefaultTracker().setArgs(biggestFragment=attrs[1], pending=attrs[3], receivedEnd=attrs[3])
        return tracker