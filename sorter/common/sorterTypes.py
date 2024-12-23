import csv
import os
import math
from enum import Enum
from entryParsing.reducedEntries import EntryAppIDName
from packetTracker.multiTracker import MultiTracker
from packetTracker.packetTracker import PacketTracker
from entryParsing.common.utils import nextRow
from packetTracker.tracker import TrackerInterface

class SorterType(Enum):
    PLAYTIME = 0
    INDIE = 1
    CONSOLIDATOR_PLAYTIME = 2
    CONSOLIDATOR_INDIE = 3
    CONSOLIDATOR_PERCENTILE = 4

    def initializeTracker(self) -> TrackerInterface:
        match self:
            case SorterType.PLAYTIME | SorterType.INDIE:
                return PacketTracker(int(os.getenv('NODE_COUNT')), int(os.getenv('NODE_ID')))
            case _:
                return MultiTracker() 

    def loadTracker(self, row) -> TrackerInterface:
        match self:
            case SorterType.PLAYTIME | SorterType.INDIE:
                return PacketTracker.fromStorage(int(os.getenv('NODE_COUNT')), int(os.getenv('NODE_ID')), row)
            case _:
                return MultiTracker.fromStorage(row)  
           
    def requireController(self) -> bool:
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

        currEntry = nextRow(topEntries)
        filepath = os.getenv('LISTENING_QUEUE') + f'filtering.tmp'
        entryIndex = 0
        with open(filepath, 'w+') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
            while currEntry is not None and entryIndex < index:
                writer.writerow(EntryAppIDName.fromAnother(currEntry).__dict__.values())
                entryIndex +=1
                currEntry = nextRow(topEntries)
    
            writer.writerow(EntryAppIDName.fromAnother(currEntry).__dict__.values())
            followingEntry = nextRow(topEntries)

            while currEntry is not None and followingEntry is not None and currEntry.getCount() == followingEntry.getCount():
                writer.writerow(EntryAppIDName.fromAnother(followingEntry).__dict__.values())
                followingEntry = nextRow(topEntries)
        
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