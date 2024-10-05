import os
from entryParsing.common.header import Header
from entryParsing.common.utils import maxDataBytes, serializeAndFragmentWithSender
from entryParsing.entryNameAvgPlaytime import EntryNameAvgPlaytime
from packetTracker.multiTracker import MultiTracker
from sorter.common.sorter import Sorter

# should get from env file
TOP_AMOUNT = 10

"""
in charge on finding the top 5 local indie games with most positive reviews
it receives packages with fragment number % amount of nodes = node id
For query 2
"""
class SorterConsolidatorAvgPlaytime(Sorter):
    def __init__(self, topAmount: int = TOP_AMOUNT): # for testing purposes
        priorNodeCount = os.getenv('SORT_AVG_PT_COUNT')
        nodeID = os.getenv('NODE_ID')
        super().__init__(id=nodeID, type=os.getenv('CONS_SORT_AVG_PT'), headerType=Header, entryType=EntryNameAvgPlaytime, 
                         topAmount=topAmount, tracker=MultiTracker(priorNodeCount))

    def getBatchTop(self, batch: list[EntryNameAvgPlaytime]) -> list[EntryNameAvgPlaytime]:
        sortedBatch = self._entryType.sort(batch)
        return sortedBatch[:self._topAmount]
    
    def _serializeAndFragment(self):
        serializeAndFragmentWithSender(maxDataBytes(), self._partialTop, self._id)
    
    def _sendToNextStep(self, data: bytes):
        self._internalComunnication.sendToAvgPlaytimeSorterConsolidator(data)