import os
import math
from enum import Enum
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entrySorterTopFinder import EntrySorterTopFinder
from packetTracker.multiTracker import MultiTracker
from packetTracker.packetTracker import PacketTracker
from entryParsing.common.utils import maxDataBytes, serializeAndFragmentWithQueryNumber, serializeAndFragmentWithSender

class SorterType(Enum):
    PLAYTIME = 0
    INDIE = 1
    CONSOLIDATOR_PLAYTIME = 2
    CONSOLIDATOR_INDIE = 3
    CONSOLIDATOR_PERCENTILE = 4

    def initializeTracker(self) -> PacketTracker:
        match self:
            case SorterType.PLAYTIME | SorterType.INDIE:
                return PacketTracker(int(os.getenv('NODE_COUNT')), int(os.getenv('NODE_ID')))
            case _:
                return MultiTracker(int(os.getenv('PRIOR_NODE_COUNT')))
    
    def topHasCapacity(self, newElementsAmount: int, topAmount: int):
        match self:
            case SorterType.CONSOLIDATOR_PERCENTILE:
                return True
            case _:
                return newElementsAmount < topAmount
        
    def getBatchTop(self, batch: list[EntrySorterTopFinder], topAmount: int, entryType: type):
        match self:
            case SorterType.CONSOLIDATOR_PERCENTILE:
                return entryType.sort(batch, False)
            case _:
                sortedBatch = entryType.sort(batch, True)
                return sortedBatch[:topAmount]
        

    def updatePartialTop(self, newOrderedList: list[EntrySorterTopFinder], topAmount: int):
        match self:
            case SorterType.CONSOLIDATOR_PERCENTILE:
                return newOrderedList
            case _:
                return newOrderedList[:topAmount]
        
    def mustElementGoFirst(self, first: EntrySorterTopFinder, other: EntrySorterTopFinder):
        greaterThan = first.isGreaterThan(other)
        match self:
            case SorterType.CONSOLIDATOR_PERCENTILE:
                return not greaterThan
            case _:
                return greaterThan

    def filterByPercentile(self, packets: list[EntrySorterTopFinder]):
        if not packets:
            return packets

        index = max(0, math.ceil(int(os.getenv('PERCENTILE')) / 100 * len(packets)) - 1)
        if index >= len(packets):
            index = len(packets) - 1

        while index > 0 and packets[index].getCount() == packets[index-1].getCount():
            index -= 1
        
        return packets[index:]
    
    def removeCountFromEntries(self, packets: list[EntrySorterTopFinder]):
        newEntries = []
        for entry in packets:
            newEntries.append(EntryAppIDName(entry.getAppID(), entry.getName()))
        return newEntries

    
    def serializeAndFragment(self, clientId: bytes, packets: list[EntrySorterTopFinder], headerType: type):
        match self:
            case SorterType.PLAYTIME | SorterType.INDIE:
                packets, _ = serializeAndFragmentWithSender(maxDataBytes=maxDataBytes(headerType), 
                                                            data=packets, 
                                                            clientId=clientId, 
                                                            senderId=int(os.getenv('NODE_ID')))
                return packets
            case _:
                return serializeAndFragmentWithQueryNumber(maxDataBytes=maxDataBytes(headerType), 
                                                           data=packets, 
                                                           clientId=clientId, 
                                                           queryNumber=int(os.getenv('QUERY_NUMBER')))
    
    def preprocessPackets(self, packets: list[EntrySorterTopFinder]):
        match self:
            case SorterType.CONSOLIDATOR_PERCENTILE:
                packets = self.filterByPercentile(packets)
                return self.removeCountFromEntries(packets)
            case _:
                return packets
        