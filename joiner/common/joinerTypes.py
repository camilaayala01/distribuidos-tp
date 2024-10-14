from enum import Enum
from entryParsing.common.header import Header
from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.entry import EntryInterface
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryAppIDNameReviewCount import EntryAppIDNameReviewCount
from entryParsing.entryAppIDNameReviewText import EntryAppIDNameReviewText
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from entryParsing.entryAppIDReviewText import EntryAppIDReviewText
from entryParsing.entryNameReviewCount import EntryNameReviewCount

class JoinerType(Enum):
    PERCENTILE = 0
    INDIE = 1
    ENGLISH = 2

    def headerType(self) -> type:
        return HeaderWithTable
    
    def gamesEntryType(self) -> type:
        return EntryAppIDName

    def reviewsEntryType(self) -> type:
        match self:
            case JoinerType.ENGLISH:
                return EntryAppIDReviewText
            case _:
                return EntryAppIDReviewCount
                
    def defaultEntry(self, name: str):
        match self:
            case JoinerType.ENGLISH:
                return []
            case _:
                return EntryNameReviewCount(name, 0)
                
    def applyJoining(self, id, name, priorJoined, review):
        match self:
            case JoinerType.ENGLISH:
                priorJoined.append(EntryAppIDNameReviewText(id, name, review.getReviewText()))
            case _:
                priorJoined.addToCount(review.getCount())

        print(priorJoined)
        return priorJoined

    def entriesForEnglish(self, joinedEntries, isDone):
        # no matter if it is done, if some entries are joined it will send them
        return [value for values in joinedEntries.values() for value in values]
    
    def entriesForIndie(self, joinedEntries, isDone):
        if not isDone:
            return []
        return joinedEntries.values()

    def entriesForPercentile(self, joinedEntries, isDone):
        if not isDone:
            return []
        entries = []
        for id, entry in joinedEntries.items():
            entries.append(EntryAppIDNameReviewCount(id, entry.getName(), entry.getCount()))
        return entries

    def entriesToSend(self, joinedEntries, isDone)-> list[EntryInterface]: 
        match self:
            case JoinerType.ENGLISH:
                return self.entriesForEnglish(joinedEntries, isDone)
            case JoinerType.INDIE:
                return self.entriesForIndie(joinedEntries, isDone)
            case JoinerType.PERCENTILE:
                return self.entriesForPercentile(joinedEntries, isDone)
    
    def getResultingHeader(self, header: Header) -> EntryInterface:
        # only to allow easy changes
        return header
            
    