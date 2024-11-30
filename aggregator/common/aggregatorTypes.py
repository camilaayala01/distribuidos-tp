import csv
from enum import Enum
import os
from entryParsing.common.headerInterface import HeaderInterface
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.common.utils import nextRow
from entryParsing.entry import EntryInterface
from entryParsing.entryOSCount import EntryOSCount
from packetTracker.defaultTracker import DefaultTracker
from packetTracker.multiTracker import MultiTracker
from packetTracker.packetTracker import PacketTracker

class AggregatorTypes(Enum):
    OS = 0
    ENGLISH = 1
    INDIE = 2
    
    def initializeTracker(self) -> PacketTracker:
        match self:
            case AggregatorTypes.OS:
                return DefaultTracker()
            case _:
                return MultiTracker()
            
    def getInitialResults(self):
        match self:
            case AggregatorTypes.ENGLISH:
                return {}
            case AggregatorTypes.OS:
                return EntryOSCount(0,0,0,0)
            case _:
                return None

    def storeEntry(self, entry: EntryInterface, storageFile):
        writer = csv.writer(storageFile, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(entry.__dict__.values())

    def getEnglishCountResults(self, entries: list[EntryInterface], priorEntriesGenerator, storageFile):
        toSend = []
        requiredReviews = int(os.getenv('REQUIRED_REVIEWS'))
        
        batch = {entry.getAppID(): entry for entry in entries} 
        
        while True:
            priorEntry = nextRow(priorEntriesGenerator)
            if priorEntry is None:
                break

            id = priorEntry.getAppID()
            if priorEntry.getCount() >= requiredReviews:
                batch.pop(id, None)
                continue
                
            entry = batch.get(id, None)
            if entry is None:
                entryToWrite = priorEntry
            else:
                priorEntry.addToCount(entry.getCount())
                entryToWrite = priorEntry
                if priorEntry.getCount() >= requiredReviews:
                    toSend.append(priorEntry) 
            
            batch.pop(id, None)
            self.storeEntry(entryToWrite, storageFile)
            
        for remainingEntry in batch.values():
            if remainingEntry.getCount() >= requiredReviews:
                toSend.append(priorEntry) 
            self.storeEntry(remainingEntry, storageFile)

        return toSend

    def getOSCountResults(self, entry: EntryInterface, priorEntriesGenerator, storageFile, isDone: bool):
        priorResult = nextRow(priorEntriesGenerator)
        if priorResult is None:
            priorResult = self.getInitialResults()
        priorResult.sumEntry(entry[0]) # only receives 1 in vector
        self.storeEntry(priorResult, storageFile)
        if not isDone:
            return []
        return [priorResult]
    
    def handleResults(self, entries: list[EntryInterface], priorEntriesGenerator, storageFile, isDone: bool) -> list[EntryInterface]:
        match self:
            case AggregatorTypes.ENGLISH:
                return self.getEnglishCountResults(entries, priorEntriesGenerator, storageFile)
            case AggregatorTypes.OS:
                return self.getOSCountResults(entries, priorEntriesGenerator, storageFile, isDone)
            case AggregatorTypes.INDIE:
                # update fragment
                return entries

    def getResultingHeader(self, header: HeaderInterface) -> EntryInterface:
        match self:
            case AggregatorTypes.OS | AggregatorTypes.ENGLISH:
                return HeaderWithQueryNumber.fromAnother(header, _queryNumber=int(os.getenv('QUERY_NUMBER')))
            case _:
                return header