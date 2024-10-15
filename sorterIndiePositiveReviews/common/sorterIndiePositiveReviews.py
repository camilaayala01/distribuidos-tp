import os
import logging
from entryParsing.common.header import Header
from entryParsing.common.utils import maxDataBytes, serializeAndFragmentWithSender
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from packetTracker.packetTracker import PacketTracker
from sorter.common.sorter import Sorter

"""
in charge on finding the top 5 local indie games with most positive reviews
it receives packages with fragment number % amount of nodes = node id
For query 3
"""
class SorterIndiePositiveReviews(Sorter):
    def __init__(self, topAmount): # for testing purposes
        nodeCount = os.getenv('SORT_INDIE_POS_REV_COUNT')
        nodeID = os.getenv('NODE_ID')
        super().__init__(id=nodeID, type=os.getenv('SORT_INDIE_POS_REV'), headerType=Header, 
                    entryType=EntryNameReviewCount, topAmount=topAmount, tracker=PacketTracker(int(nodeCount), int(nodeID)))
        self._id = int(nodeID)
        
    def getBatchTop(self, batch: list[EntryNameReviewCount]) -> list[EntryNameReviewCount]:
        sortedBatch = self._entryType.sort(batch, True)
        return sortedBatch[:self._topAmount]
    
    def _serializeAndFragment(self):
        packets, _ = serializeAndFragmentWithSender(maxDataBytes(self._headerType), self._partialTop, self._id)
        return packets
        
    def _sendToNextStep(self, data: bytes):
        self._internalCommunication.sendToPositiveReviewsSorterConsolidator(data)
        logging.info(f'action: send final results to consolidator | result: success')