from enum import Enum
from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface
from entryParsing.entryAppIDNameReviewCount import EntryAppIDNameReviewCount
from entryParsing.entryAppIDNameReviewText import EntryAppIDNameReviewText
from entryParsing.entryNameReviewCount import EntryNameReviewCount

REQUIRED_ENTRIES = 5000

class JoinerType(Enum):
    PERCENTILE = 0
    INDIE = 1
    ENGLISH = 2
                
    def defaultEntry(self, name: str):
        match self:
            case JoinerType.ENGLISH:
                return []
            case _:
                return EntryNameReviewCount(name, 0)
                
    def applyJoining(self, id, name, priorJoined, review):
        #abrir archivo joinedEntries
        match self:
            case JoinerType.ENGLISH:
                priorJoined.append(EntryAppIDNameReviewText(id, name, review.getReviewText()))
            case _:
                priorJoined.addToCount(review.getCount()) 
        return priorJoined

    def entriesForEnglish(self, joinedEntries):
        # manda todas a la capa siguiente y vacia las joined
        joinedEntries = [item for sublist in joinedEntries.values() for item in sublist]
        return joinedEntries, {}
    
    def entriesForIndie(self, joinedEntries, isDone):
        if not isDone:
            return [], joinedEntries
        return joinedEntries.values(), {}

    def entriesForPercentile(self, joinedEntries, isDone):
        entries = []
        if isDone:
            for id, entry in joinedEntries.items():
                entries.append(EntryAppIDNameReviewCount.fromAnother(entry, _appID=id))
            joinedEntries = {}
        return entries, joinedEntries

    # returns a tuple of entries to send, joined entries, sent ids that will be ignored from now on
    def entriesToSend(self, joinedEntries, isDone): 
        match self:
            case JoinerType.ENGLISH:
                return self.entriesForEnglish(joinedEntries)
            case JoinerType.INDIE:
                return self.entriesForIndie(joinedEntries, isDone)
            case JoinerType.PERCENTILE:
                return self.entriesForPercentile(joinedEntries, isDone)
    