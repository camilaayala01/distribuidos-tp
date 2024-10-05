import os
from entryParsing.common.header import Header
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.common.utils import maxDataBytes, serializeAndFragmentWithSender
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from packetTracker.packetTracker import PacketTracker
from sorterTopFinder.common.sorterTopFinder import SorterTopFinder

"""
in charge on finding the top 5 local indie games with most positive reviews
it receives packages with fragment number % amount of nodes = node id
For query 3
"""
class SorterIndiePositiveReviews(SorterTopFinder):
    def __init__(self, topAmount): # for testing purposes
        nodeCount = os.getenv('SORT_INDIE_POS_REV_COUNT')
        nodeID = os.getenv('NODE_ID')
        super().__init__(id=nodeID, type=os.getenv('SORT_INDIE_POS_REV'), headerType=Header, 
                    entryType=EntryNameReviewCount, topAmount=topAmount, tracker=PacketTracker(nodeCount, nodeID))
        
    def getBatchTop(self, batch: list[EntryNameReviewCount]) -> list[EntryNameReviewCount]:
        sortedBatch = self._entryType.sort(batch, True)
        return sortedBatch[:self._topAmount]
    
    def _serializeAndFragment(self):
        serializeAndFragmentWithSender(maxDataBytes(), self._partialTop, self._id)
        
    def _sendToNextStep(self, data: bytes):
        self._internalComunnication.sendToPositiveReviewsSorterConsolidator(data)