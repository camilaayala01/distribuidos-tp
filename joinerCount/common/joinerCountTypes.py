from enum import Enum
import os

from entryParsing.common.header import Header
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.entry import EntryInterface
from entryParsing.entryAppIDNameReviewCount import EntryAppIDNameReviewCount
from entryParsing.entryName import EntryName
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from entryParsing.entryOSCount import EntryOSCount

class JoinerCountType(Enum):
    OS = 0
    ENGLISH = 1

    def headerType(self) -> type:
        return Header
    
    def entryType(self) -> type:
        match self:
            case JoinerCountType.ENGLISH:
                return EntryAppIDNameReviewCount
            case JoinerCountType.OS:
                return EntryOSCount
            
    def getInitialResults(self):
        match self:
            case JoinerCountType.ENGLISH:
                return {}
            case JoinerCountType.OS:
                return EntryOSCount(0,0,0,0)
      
    def getEnglishCountResults(self, priorResults, entries, sent):
        toSend = []
        for entry in entries:
            id = entry.getAppID()
            if id in sent:
                continue

            priorEntry = priorResults.get(id, EntryNameReviewCount(entry.getName(), 0))
            if priorEntry.getCount() + entry.getCount() >= int(os.getenv('REQUIRED_REVIEWS')):
                toSend.append(EntryName(priorEntry.getName()))
                sent.add(id)
                priorResults.pop(id, None)
            else:
                priorEntry.addToCount(entry.getCount())
                priorResults[id] = priorEntry

        return toSend, priorResults, sent

    def getOSCountResults(self, priorResult, entry, isDone):
        priorResult.sumEntry(entry)
        if not isDone:
            return [], priorResult, set()
        return [priorResult], self.getInitialResults(), set()
        
    # returns toSend, joinedEntries, sent set
    def handleResults(self, entries, priorResult, isDone, sent):
        match self:
            case JoinerCountType.ENGLISH:
                return self.getEnglishCountResults(priorResult, entries, sent)
            case JoinerCountType.OS:
                return self.getOSCountResults(priorResult, entries, isDone) 

    def getResultingHeader(self, fragnum: int, isDone: bool) -> EntryInterface:
        match self:
            case JoinerCountType.ENGLISH:
                return HeaderWithSender(int(os.getenv('NODE_ID')), fragnum, isDone)
            case JoinerCountType.OS:
                return HeaderWithQueryNumber(fragnum, True, int(os.getenv('QUERY_NUMBER')))
                
               
