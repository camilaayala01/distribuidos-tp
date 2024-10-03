from abc import ABC, abstractmethod
import os
from entryParsing.common.header import Header
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.common.utils import maxDataBytes
from entryParsing.entrySorterTopFinder import EntrySorterTopFinder
from internalCommunication.internalCommunication import InternalCommunication
from packetTracker.packetTracker import PacketTracker

TOP_AMOUNT = 5

class SorterTopFinder(ABC):
    def __init__(self, id: int, nodeCount: int, type: str, entrySorter: type, topAmount: int):
        self._internalComunnication = InternalCommunication(os.getenv(type), os.getenv('NODE_ID'))
        self._entrySorter = entrySorter
        self._partialTop = []
        self._topAmount = topAmount
        self._id = id
        self._packetTracker = PacketTracker(nodeCount, id)

    def execute(self, data: bytes):
        # communication is not developed
        print("work in progress")

    @abstractmethod
    def getBatchTop(self, batch: list[EntrySorterTopFinder]) -> list[EntrySorterTopFinder]:
        pass

    def reset(self):
        self._partialTop = []
        self._packetTracker.reset()

    def topHasCapacity(self, mergedList):
        return len(mergedList) < self._topAmount
        
    def updatePartialTop(self, newOrderedList):
        self._partialTop = newOrderedList[:self._topAmount]

    def mustElementGoFirst(self, first: EntrySorterTopFinder, other: EntrySorterTopFinder):
        return first.isGreaterThan(other)

    def mergeKeepTop(self, batch: list[EntrySorterTopFinder]):
        if len(batch) == 0:
            return
        
        newBatchTop = self.getBatchTop(batch)

        i, j = 0, 0
        mergedList = []

        while i < len(self._partialTop) and j < len(newBatchTop):
            if self.mustElementGoFirst(self._partialTop[i], newBatchTop[j]):
                mergedList.append(self._partialTop[i])
                i += 1
            else:
                mergedList.append(newBatchTop[j])
                j += 1
        
        if self.topHasCapacity(mergedList):
            # only 1 will have elements
            mergedList.extend(self._partialTop[i:])
            mergedList.extend(newBatchTop[j:])

        self.updatePartialTop(mergedList)
            
    """returns serialized data"""
    def serializeTop(self, maxDataBytes)-> list[bytes]: # recv max data bytes for testing purposes
        fragment = 1
        packets = []
        currPacket = bytes()

        for entry in self._partialTop:
            entryBytes = entry.serialize()
            if len(currPacket) + len(entryBytes) <= maxDataBytes:
                currPacket += entryBytes
            else:
                headerBytes = HeaderWithSender(self._id, fragment, False).serialize()
                fragment += 1
                packets.append(headerBytes + currPacket)
                currPacket = entryBytes

        packets.append(HeaderWithSender(self._id, fragment, True).serialize() + currPacket)
        return packets

    def _sendToNextStep(self):
        if not self._packetTracker.isDone():
            return
        packets = self.serializeTop(maxDataBytes(HeaderWithSender))
        # send packets
        self.reset()

    def _processBatch(self, batch: bytes):
        header, batch = Header.deserialize(batch)
        if self._packetTracker.isDuplicate(header):
            return
        self._packetTracker.update(header)
        entries = self._entrySorter.deserialize(batch)
        self.mergeKeepTop(entries)
        self._sendToNextStep()
