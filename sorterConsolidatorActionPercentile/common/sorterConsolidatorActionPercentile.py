import os
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.common.utils import maxDataBytes, serializeAndFragmentWithQueryNumber
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from packetTracker.multiTracker import MultiTracker
from sorterTopFinder.common.sorterTopFinder import SorterTopFinder

"""
in charge on finding the 90th percentile of negative reviews
it is only one node that needs to find and sort all entries
For query 5
"""
class SorterConsolidatorActionPercentile(SorterTopFinder):
    def __init__(self):
        priorNodeCount = os.getenv('JOIN_ACT_NEG_REV_COUNT')
        nodeID = os.getenv('NODE_ID')
        super().__init__(id=nodeID, type=os.getenv('SORT_CONS_PERCENTILE'), headerType=HeaderWithSender, 
                         entryType=EntryNameReviewCount, topAmount=None, tracker=MultiTracker(int(priorNodeCount)))

    def _serializeAndFragment(self):
        serializeAndFragmentWithQueryNumber(maxDataBytes(), self._partialTop, 5)

    def getBatchTop(self, batch: list[EntryNameReviewCount]) -> list[EntryNameReviewCount]:
        return self._entryType.sort(batch, False)
    
    def mustElementGoFirst(self, first: EntryNameReviewCount, other: EntryNameReviewCount):
        return not first.isGreaterThan(other)

    def topHasCapacity(self, mergedList):
        return True

    def updatePartialTop(self, newOrderedList):
        self._partialTop = newOrderedList

    def _sendToNextStep(self, data: bytes):
        print("sorter joiner for this node is not yet implemented")
        # self._internalComunnication.sendToPositiveReviewsActionGamesJoiner(str(i), msg)