import os
from enum import Enum
from entryParsing.common.header import Header
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.entryAppIDNameReviewCount import EntryAppIDNameReviewCount
from entryParsing.entry import EntryInterface
from entryParsing.entryOSCount import EntryOSCount

class JoinerCountType(Enum):
    OS = 0
    ENGLISH = 1

    def entryType(self) -> type:
        match self:
            case JoinerCountType.OS:
                return EntryOSCount
            case JoinerCountType.ENGLISH:
                return EntryAppIDNameReviewCount

    def headerType(self) -> type:
        return Header
    
    def getDefaultEntry(self)-> EntryInterface:
        match self:
            case JoinerCountType.OS:
                return EntryOSCount(0, 0, 0)
            case JoinerCountType.ENGLISH:
                return {}

    def sumForOs(self, incoming, prior):
        prior._windows += incoming.getWindowsCount()
        prior._mac += incoming.getMacCount()
        prior._linux += incoming.getLinuxCount()
        prior._total += incoming.getTotalCount()
        return prior
    
    def sumEnglish(self, incoming, prior):
        pass
        # for entry in incoming:
        #     appID = entry.getAppID()
        #     priorEntry = prior.get(appID, EntryAppIDNameReviewCount(entry.getName(), 0))
        #     if priorEntry.getCount() + entry.getCount() >= os.getenv('REQUIRED_ENTRIES'):
        #         ready.append(EntryName(priorEntry.getName()))
        #         self._sent.add(appID)
        #         self._counts.pop(appID, None)
        #     else:
        #         priorEntry.addToCount(entry.getCount())
        #         self._counts[appID] = priorEntry
            
    def applySum(self, entry, priorCounts) -> EntryInterface:
        match self: 
            case JoinerCountType.OS:
                self.sumForOs(entry, priorCounts)
            case JoinerCountType.ENGLISH:
                self.sumEnglish(entry, priorCounts)
            
    def getResultingHeader(self, header: Header) -> EntryInterface:
        match self:
            case JoinerCountType.OS:
                return HeaderWithQueryNumber(fragment=1, eof=True, queryNumber=1)
            case JoinerCountType.ENGLISH:
                return header