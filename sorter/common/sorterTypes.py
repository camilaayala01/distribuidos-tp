import csv
import os
import math
from enum import Enum
from entryParsing.common.fieldParsing import getClientIdUUID
from entryParsing.entryAppIDName import EntryAppIDName
from packetTracker.multiTracker import MultiTracker
from packetTracker.packetTracker import PacketTracker
from entryParsing.common.utils import nextEntry

class SorterType(Enum):
    PLAYTIME = 0
    INDIE = 1
    CONSOLIDATOR_PLAYTIME = 2
    CONSOLIDATOR_INDIE = 3
    CONSOLIDATOR_PERCENTILE = 4

    def initializeTracker(self, clientId: bytes) -> PacketTracker:
        match self:
            case SorterType.PLAYTIME | SorterType.INDIE:
                return PacketTracker(int(os.getenv('NODE_COUNT')), int(os.getenv('NODE_ID')), getClientIdUUID(clientId))
            case _:
                return MultiTracker(int(os.getenv('PRIOR_NODE_COUNT')), getClientIdUUID(clientId))        

    def requireController(self) -> PacketTracker:
        match self:
            case SorterType.PLAYTIME | SorterType.INDIE:
                return True
            case _:
                return False 

    def filterByPercentile(self, topEntries, topAmount):
        if topAmount == 0:
            return topEntries

        index = min(topAmount - 1, math.floor((100 - int(os.getenv('PERCENTILE'))) / 100 * topAmount))
        if index < 0:
            index = 0

        currEntry = nextEntry(topEntries)
        filepath = os.getenv('LISTENING_QUEUE') + f'filtering.tmp'
        entryIndex = 0
        with open(filepath, 'w+') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
            while currEntry is not None and entryIndex < index:
                writer.writerow(EntryAppIDName.fromAnother(currEntry).__dict__.values())
                entryIndex +=1
                currEntry = nextEntry(topEntries)
    
            writer.writerow(EntryAppIDName.fromAnother(currEntry).__dict__.values())
            followingEntry = nextEntry(topEntries)

            while currEntry is not None and followingEntry is not None and currEntry.getCount() == followingEntry.getCount():
                writer.writerow(EntryAppIDName.fromAnother(followingEntry).__dict__.values())
                followingEntry = nextEntry(topEntries)
        
        with open(filepath, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                yield EntryAppIDName.fromArgs(row)
    
    def extraParamsForHeader(self):
        match self:
            case SorterType.PLAYTIME | SorterType.INDIE:
                return {"_sender": int(os.getenv('NODE_ID'))}
            case _:
                return {"_queryNumber": int(os.getenv('QUERY_NUMBER'))}
            
    def preprocessPackets(self, topEntries, topAmount):
        match self:
            case SorterType.CONSOLIDATOR_PERCENTILE:
                topEntries = self.filterByPercentile(topEntries, topAmount)
                return topEntries
            case _:
                return topEntries