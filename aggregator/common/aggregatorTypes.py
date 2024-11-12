import csv
from enum import Enum
import os
from entryParsing.common.fieldParsing import getClientIdUUID
from entryParsing.common.headerInterface import HeaderInterface
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.common.utils import nextEntry
from entryParsing.entry import EntryInterface
from entryParsing.entryName import EntryName
from entryParsing.entryOSCount import EntryOSCount
from packetTracker.defaultTracker import DefaultTracker
from packetTracker.multiTracker import MultiTracker
from packetTracker.packetTracker import PacketTracker

class AggregatorTypes(Enum):
    OS = 0
    ENGLISH = 1
    INDIE = 2
    
    def initializeTracker(self, clientId: bytes) -> PacketTracker:
        match self:
            case AggregatorTypes.OS:
                return DefaultTracker(getClientIdUUID(clientId))
            case _:
                return MultiTracker(int(os.getenv('PRIOR_NODE_COUNT')), getClientIdUUID(clientId))
            
    def getInitialResults(self):
        match self:
            case AggregatorTypes.ENGLISH:
                return {}
            case AggregatorTypes.OS:
                return EntryOSCount(0,0,0,0)
            case _:
                return None

    def storeEntry(self, entry: EntryInterface, priorResultsPath):
        filepath = f'{priorResultsPath}.tmp'
        with open(filepath, 'a+') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(entry.__dict__.values())
    
    def loadEntries(self, entryType, priorResultsPath):
        filepath = f'{priorResultsPath}.csv'
        if not os.path.exists(filepath):
            return iter([])
        
        with open(filepath, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                try:
                    yield entryType.fromArgs(row)
                except Exception as e:
                    print("exception", e)
                    print(row)
      
    def saveNewResults(self, priorResultsPath):
        if os.path.exists(priorResultsPath + '.tmp'):
            os.rename(priorResultsPath + '.tmp', priorResultsPath + '.csv')

    def getEnglishCountResults(self, entryType, priorResultsPath, entries: list[EntryInterface]):
        toSend = []
        requiredReviews = int(os.getenv('REQUIRED_REVIEWS'))
        if not len(entries):
            return []
        batch = {entry.getAppID(): entry for entry in entries} 
        generator = self.loadEntries(entryType, priorResultsPath)
        
        while True:
            priorEntry = nextEntry(generator)
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
                    toSend.append(EntryName(priorEntry.getName()))
            
            batch.pop(id, None)
            self.storeEntry(entryToWrite, priorResultsPath)
            
        for remainingEntry in batch.values():
            if remainingEntry.getCount() >= requiredReviews:
                toSend.append(EntryName(priorEntry.getName()))
            self.storeEntry(remainingEntry, priorResultsPath)
        
        self.saveNewResults(priorResultsPath)
        return toSend

    def getOSCountResults(self, entryType, priorResultsPath, entry, isDone):
        generator = self.loadEntries(entryType, priorResultsPath)
        priorResult = nextEntry(generator)
        if priorResult is None:
            priorResult = self.getInitialResults()
        priorResult.sumEntry(entry)
        self.storeEntry(priorResult, priorResultsPath)
        os.rename(priorResultsPath + '.tmp', priorResultsPath + '.csv')
        if not isDone:
            return []
        return [priorResult]
    
    def handleResults(self, entries, entryType, priorResultsPath, isDone) -> list[EntryInterface]:
        match self:
            case AggregatorTypes.ENGLISH:
                return self.getEnglishCountResults(entryType, priorResultsPath, entries)
            case AggregatorTypes.OS:
                return self.getOSCountResults(entryType, priorResultsPath, entries, isDone)
            case AggregatorTypes.INDIE:
                return entries

    def getResultingHeader(self, header: HeaderInterface) -> EntryInterface:
        match self:
            case AggregatorTypes.OS | AggregatorTypes.ENGLISH:
                return HeaderWithQueryNumber.fromAnother(header, _queryNumber=int(os.getenv('QUERY_NUMBER')))
            case _:
                return header
                
               
