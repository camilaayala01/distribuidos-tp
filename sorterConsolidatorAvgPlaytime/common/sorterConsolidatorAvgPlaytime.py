import os
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.common.utils import maxDataBytes, serializeAndFragmentWithQueryNumber
from entryParsing.entryNameAvgPlaytime import EntryNameAvgPlaytime
from packetTracker.multiTracker import MultiTracker
from sorter.common.sorter import Sorter

"""
in charge on finding the top 5 indie games with most positive reviews
must wait for responses from all prior sorter nodes
For query 2
"""
class SorterConsolidatorAvgPlaytime(Sorter):
    def __init__(self, topAmount: int): # for testing purposes
        priorNodeCount = os.getenv('SORT_AVG_PT_COUNT')
        super().__init__(type=os.getenv('CONS_SORT_AVG_PT'), headerType=HeaderWithSender, entryType=EntryNameAvgPlaytime, 
                         topAmount=topAmount, tracker=MultiTracker(priorNodeCount))

    def getBatchTop(self, batch: list[EntryNameAvgPlaytime]) -> list[EntryNameAvgPlaytime]:
        sortedBatch = self._entryType.sort(batch)
        return sortedBatch[:self._topAmount]
    
    def _serializeAndFragment(self):
        serializeAndFragmentWithQueryNumber(maxDataBytes(), self._partialTop, 3)
    
    def _sendToNextStep(self, data: bytes):
        self._internalComunnication.sendToAvgPlaytimeSorterConsolidator(data)