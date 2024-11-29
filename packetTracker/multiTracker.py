from entryParsing.common.headerWithSender import HeaderWithSender
from packetTracker.defaultTracker import DefaultTracker
from packetTracker.tracker import TrackerInterface

class MultiTracker(TrackerInterface):
    def __init__(self, trackers: dict = dict()):
        # sender: defaultTracker
        self._trackers = trackers
    
    def getProcessingTracker(self, header: HeaderWithSender):
        self._trackers[header.getSenderID()] = self._trackers.get(header.getSenderID(), DefaultTracker())
        return self._trackers[header.getSenderID()]
    
    def isDuplicate(self, header: HeaderWithSender):
        if self.getProcessingTracker(header).isDuplicate(header):
            print("Tracker state: ", self._trackers)
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
    
    #[senderId,biggestFragment,pending,receivedEnd],[senderId,biggestFragment,pending,receivedEnd]
    @classmethod
    def fromStorage(cls, row: list[str]):
        trackers = {}
        for tracker in row:
            attrs = eval(tracker)
            trackers[attrs[0]] = DefaultTracker().setArgs(biggestFragment=attrs[1], pending=attrs[3], receivedEnd=attrs[3])
        return cls(trackers)