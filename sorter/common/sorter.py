from abc import ABC, abstractmethod
import os
from entryParsing.common.header import Header
from entryParsing.entrySorterTopFinder import EntrySorterTopFinder
from internalCommunication.internalCommunication import InternalCommunication
from packetTracker.packetTracker import PacketTracker

class Sorter(ABC):
    def __init__(self, id: str, type: str, headerType: type, entryType: type, topAmount: int, tracker: PacketTracker):
        self._internalCommunication = InternalCommunication(type, id)
        self._entryType = entryType
        self._headerType = headerType
        self._partialTop = []
        self._topAmount = topAmount
        self._packetTracker = tracker

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

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

    @abstractmethod
    def _sendToNextStep(self, data: bytes):
        pass

    @abstractmethod
    def _serializeAndFragment(self):
        pass
        
    def _handleSending(self):
        if not self._packetTracker.isDone():
            return
        packets = self._serializeAndFragment()
        for pack in packets:
            self._sendToNextStep(pack)
        self.reset()

    def handleMessage(self, ch, method, properties, body):
        header, batch = self._headerType.deserialize(body)
        if self._packetTracker.isDuplicate(header):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
        self._packetTracker.update(header)
        entries = self._entryType.deserialize(batch)
        self.mergeKeepTop(entries)
        self._handleSending()
        ch.basic_ack(delivery_tag = method.delivery_tag)

