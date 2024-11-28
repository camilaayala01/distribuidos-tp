from entryParsing.common.fieldParsing import readRow
from entryParsing.common.headerWithSender import HeaderWithSender
from packetTracker.defaultTracker import DefaultTracker
from packetTracker.packetTracker import PacketTracker
from packetTracker.tracker import TrackerInterface
import os 
import csv

class MultiTracker(TrackerInterface):

    def __init__(self, trackers: dict = dict()):
        self._trackers = trackers
    
    @classmethod
    def initialize(cls, filepath) -> TrackerInterface:
        trackers = {}
        generator = readRow(filepath) 
        if generator is None:
            return cls()
        trackerCount = int(next(generator))
        for i in range(trackerCount):
            row = next(generator)
            senderId = int(row[3])
            trackers[senderId] = DefaultTracker.fromStorage(row[:3])
        return cls(trackers)
    
    
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
    
    def asRows(self):
        rows = [len(self._trackers)]
        for senderId, tracker in self._trackers.items():
            rows.extend[tracker._biggestFragment, str(tracker._pending), tracker._receivedEnd, senderId]