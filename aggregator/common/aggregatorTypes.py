from enum import Enum
import os
from entryParsing.common.fieldParsing import getClientIdUUID
from entryParsing.common.headerInterface import HeaderInterface
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.entry import EntryInterface
from entryParsing.entryName import EntryName
from entryParsing.entryNameReviewCount import EntryNameReviewCount
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
      
    def getEnglishCountResults(self, priorResults, entries):
        toSend = []
        requiredReviews = int(os.getenv('REQUIRED_REVIEWS'))
        for entry in entries:
            id = entry.getAppID()

            priorEntry = priorResults.get(id, EntryNameReviewCount(entry.getName(), 0))
            if priorEntry.getCount() >= requiredReviews:
                continue
            elif priorEntry.getCount() + entry.getCount() >= requiredReviews:
                # write
                priorEntry.addToCount(entry.getCount())
                priorResults[id] = priorEntry
                # mark to be sent
                toSend.append(EntryName(priorEntry.getName()))
            else:
                # write
                priorEntry.addToCount(entry.getCount())
                priorResults[id] = priorEntry

        return toSend, priorResults

    def getOSCountResults(self, priorResult, entry, isDone):
        priorResult.sumEntry(entry)
        if not isDone:
            return [], priorResult
        return [priorResult], self.getInitialResults()
    
    def getIndieResults(self, entries):
        return entries, self.getInitialResults()
    
    # returns toSend, joinedEntries, sent set
    def handleResults(self, entries, priorResult, isDone):
        match self:
            case AggregatorTypes.ENGLISH:
                return self.getEnglishCountResults(priorResult, entries)
            case AggregatorTypes.OS:
                return self.getOSCountResults(priorResult, entries, isDone)
            case AggregatorTypes.INDIE:
                return self.getIndieResults(entries)

    def getResultingHeader(self, header: HeaderInterface) -> EntryInterface:
        match self:
            case AggregatorTypes.OS | AggregatorTypes.ENGLISH:
                return HeaderWithQueryNumber.fromAnother(header, _queryNumber=int(os.getenv('QUERY_NUMBER')))
            case _:
                return header
                
               
