import os
import math
from enum import Enum
from entryParsing.common.fieldParsing import getClientIDString
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

    def initializeTracker(self, clientId: bytes) -> PacketTracker:
        match self:
            case SorterType.PLAYTIME | SorterType.INDIE:
                return PacketTracker(int(os.getenv('NODE_COUNT')), int(os.getenv('NODE_ID')), getClientIDString(clientId))
            case _:
                return MultiTracker(int(os.getenv('PRIOR_NODE_COUNT')), getClientIDString(clientId))        

    def filterByPercentile(self, packets: list[EntrySorterTopFinder]):
        if not packets:
            return packets

        index = min(len(packets) - 1, math.floor((100 - int(os.getenv('PERCENTILE'))) / 100 * len(packets)))
        if index < 0:
            index = 0

        while index < len(packets) - 1 and packets[index].getCount() == packets[index+1].getCount():
            index += 1
        
        return packets[:index + 1]
    
    def removeCountFromEntries(self, packets: list[EntrySorterTopFinder]):
        newEntries = []
        for entry in packets:
            newEntries.append(EntryAppIDName.fromAnother(entry))
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
        