import csv
from enum import Enum
import os
from entryParsing.common.fieldParsing import getClientIdUUID
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
    
    def initializeTracker(self, clientId: bytes) -> PacketTracker:
        match self:
            case AggregatorTypes.OS:
                return DefaultTracker(getClientIdUUID(clientId))
            case _:
                return MultiTracker(getClientIdUUID(clientId))
            
    def getInitialResults(self):
        match self:
            case AggregatorTypes.ENGLISH:
                return {}
            case AggregatorTypes.OS:
                return EntryOSCount(0,0,0,0)
            case AggregatorTypes.INDIE:
                return None

    def storeEntry(self, entry: EntryInterface, priorResultsPath, fragment: int, written: int):
        filepath = f'{priorResultsPath}.tmp'
        with open(filepath, 'a+') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
            if written == 0:
                writer.writerow(fragment)
            writer.writerow(entry.__dict__.values())
        written += 1

    
    def loadState(self, entryType, priorResultsPath):
        filepath = f'{priorResultsPath}.csv'
        if not os.path.exists(filepath):
            return iter([])
        with open(filepath, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
            yield next(reader) # get fragment
            for row in reader:
                try:
                    yield entryType.fromArgs(row)
                except Exception as e:
                    print("exception", e)
                    print(row)
      
    def getFragment(self, generator) -> int:
        try:
            fragment = next(generator)
            return int(fragment)
        except StopIteration:
            return 0

    def getEnglishCountResults(self, entryType, priorResultsPath, entries: list[EntryInterface]):
        toSend = []
        requiredReviews = int(os.getenv('REQUIRED_REVIEWS'))
        if not len(entries):
            return []
        batch = {entry.getAppID(): entry for entry in entries} 
        generator = self.loadState(entryType, priorResultsPath)
        fragment = self.getFragment(generator)
        fragment += 1
        written = 0
        for priorEntry in generator:
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
            self.storeEntry(entryToWrite, priorResultsPath, fragment, written)

        for remainingEntry in batch.values():
            if remainingEntry.getCount() >= requiredReviews:
                toSend.append(priorEntry)
            self.storeEntry(remainingEntry, priorResultsPath, fragment, written)
        return toSend

    def getOSCountResults(self, entryType, priorResultsPath, entry, isDone):
        generator = self.loadState(entryType, priorResultsPath)
        fragment = self.getFragment(generator)
        fragment += 1
        priorResult = nextRow(generator)
        if priorResult is None:
            priorResult = self.getInitialResults()
        priorResult.sumEntry(entry)
        self.storeEntry(priorResult, priorResultsPath, fragment, 0)
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
            case AggregatorTypes.INDIE:
                return header