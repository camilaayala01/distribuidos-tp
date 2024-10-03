from entryParsing.common.header import Header
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from packetTracker.packetTracker import PacketTracker
from sorterTopFinder.common.sorterTopFinder import SorterTopFinder

TOP_AMOUNT = 5

# change to a call to env file or somewhere that stores this
AMOUNT_OF_SORTERS = 2
CORRESPONDING_MODULE = 0

"""in charge on finding the top 5 indie games with most positive reviews"""
class SorterIndiePositiveReviews(SorterTopFinder):
    def __init__(self, topAmount: int = TOP_AMOUNT): # for testing purposes
        super().__init__("SORT_INDIE_POS_REV", EntryNameReviewCount, topAmount)
        self._id = CORRESPONDING_MODULE
        self._packetTracker = PacketTracker(AMOUNT_OF_SORTERS, CORRESPONDING_MODULE)

    def reset(self):
        super().reset()
        self._packetTracker.reset()

    def getBatchTop(self, batch: list[EntryNameReviewCount]) -> list[EntryNameReviewCount]:
        sortedBatch = self._entrySorter.sort(batch, True)
        return sortedBatch[:self._topAmount]

    def serializeTop(self):
        
        header = Header(1, True) 

    def _sendToNextStep(self):
        if not self._packetTracker.isDone():
            return
        self.reset()
        # serialize data, see if it fits in max packet size, and send to sorter joiner

    def _processBatch(self, batch: bytes):
        header, batch = Header.deserialize(batch)
        if self._packetTracker.isDuplicate(header):
            # ignore the rest
            return
        else: 
            self._packetTracker.update(header)
        entries = self._entrySorter.deserialize(batch)
        self.mergeKeepTop(self, entries)
        self._sendToNextStep()
        # if isDone, send to next step
        # sendToNextStep