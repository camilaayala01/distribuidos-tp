import os
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.common.utils import maxDataBytes, serializeAndFragmentWithQueryNumber
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from packetTracker.multiTracker import MultiTracker
from sorter.common.sorter import Sorter

"""
in charge on finding the top 5 of all prior nodes and finding the 
global top 5
For query 3
"""
class SorterConsolidatorIndieTop(Sorter):
    def __init__(self, topAmount): # for testing purposes
        priorNodeCount = os.getenv('SORT_INDIE_POS_REV_COUNT')
        super().__init__(id=os.getenv('NODE_ID'), type=os.getenv('CONS_SORT_INDIE_POS_REV'), headerType=HeaderWithSender, 
                         entryType=EntryNameReviewCount, topAmount=topAmount, tracker=MultiTracker(priorNodeCount))
        
    def getBatchTop(self, batch: list[EntryNameReviewCount]) -> list[EntryNameReviewCount]:
        sortedBatch = self._entryType.sort(batch, True)
        return sortedBatch[:self._topAmount]
    
    def _serializeAndFragment(self):
        serializeAndFragmentWithQueryNumber(maxDataBytes(), self._partialTop, 3)
        
    def _sendToNextStep(self, data: bytes):
        self._internalComunnication.sendToDispatcher(data)