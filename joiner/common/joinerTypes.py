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
                
    def joinedEntryType(self):
        match self:
            case JoinerType.ENGLISH:
                return EntryAppIDNameReviewText
            case _:
                return EntryAppIDNameReviewCount

    def defaultEntry(self, name: str, appID: str):
        match self:
            case JoinerType.ENGLISH:
                return []
            case _:
                return EntryAppIDNameReviewCount(_appID=appID, _name=name, _reviewCount=0)
            
    def applyJoining(self, id, name, priorJoined, review):
        match self:
            case JoinerType.ENGLISH:
                priorJoined.append(EntryAppIDNameReviewText(id, name, review.getReviewText()))
            case _:
                priorJoined.addToCount(review.getCount()) 
        return priorJoined
    
    def entriesForEnglish(self, joinedEntries):
        joinedEntries = [entry for sublist in joinedEntries.values() for entry in sublist]
        if len(joinedEntries) == 0:
            return None
        return iter(joinedEntries)
    
    def entriesForIndieAndPercentile(self, isDone, activeClient):
        if not isDone:
            return None
        return activeClient.loadJoinedEntries(self.joinedEntryType())

    def storeJoinedEntries(self, joinedEntries, activeClient):
        match self:
            case JoinerType.ENGLISH:
                return 
            case _:
                activeClient.storeJoinedEntries(joinedEntries, self.joinedEntryType())

    def entriesToSend(self, joinedEntries, isDone, activeClient): 
        match self:
            case JoinerType.ENGLISH:
                return self.entriesForEnglish(joinedEntries)
            case _:
                return self.entriesForIndieAndPercentile(isDone, activeClient)
    