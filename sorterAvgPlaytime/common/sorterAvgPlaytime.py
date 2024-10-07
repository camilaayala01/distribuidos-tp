import os
from entryParsing.common.header import Header
from entryParsing.common.utils import maxDataBytes, serializeAndFragmentWithSender
from entryParsing.entryNameAvgPlaytime import EntryNameAvgPlaytime
from packetTracker.packetTracker import PacketTracker
from sorter.common.sorter import Sorter

"""
in charge on finding the top 5 local indie games with most positive reviews
it receives packages with fragment number % amount of nodes = node id
Query 2
"""
class SorterAvgPlaytime(Sorter):
    def __init__(self, topAmount: int): # for testing purposes
        nodeCount = os.getenv('SORT_AVG_PT_COUNT')
        nodeID = os.getenv('NODE_ID')
        self._id = int(nodeID)
        super().__init__(id=nodeID, type=os.getenv('SORT_AVG_PT'), headerType=Header, entryType=EntryNameAvgPlaytime, 
                         topAmount=topAmount, tracker=PacketTracker(int(nodeCount), int(nodeID)))

    def getBatchTop(self, batch: list[EntryNameAvgPlaytime]) -> list[EntryNameAvgPlaytime]:
        sortedBatch = self._entryType.sort(batch)
        return sortedBatch[:self._topAmount]
    
    def _serializeAndFragment(self):
        serializeAndFragmentWithSender(maxDataBytes(), self._partialTop, self._id)
    
    def _sendToNextStep(self, data: bytes):
        self._internalCommunication.sendToAvgPlaytimeSorterConsolidator(data)