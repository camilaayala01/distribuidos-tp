from enum import Enum
from entryParsing.reducedEntries import EntryAppIDNameReviewCount, EntryAppIDNameReviewText

class JoinerType(Enum):
    REGULAR = 0
    ENGLISH = 1
                
    def joinedEntryType(self):
        match self:
            case JoinerType.ENGLISH:
                return EntryAppIDNameReviewText
            case JoinerType.REGULAR:
                return EntryAppIDNameReviewCount

    def defaultEntry(self, name: str, appID: str):
        match self:
            case JoinerType.ENGLISH:
                return []
            case JoinerType.REGULAR:
                return EntryAppIDNameReviewCount(_appID=appID, _name=name, _reviewCount=0)
            
    def applyJoining(self, id, name, priorJoined, review):
        match self:
            case JoinerType.ENGLISH:
                priorJoined.append(EntryAppIDNameReviewText(id, name, review.getReviewText()))
            case JoinerType.REGULAR:
                priorJoined.addToCount(review.getCount()) 
        return priorJoined
    
    def entriesForEnglish(self, joinedEntries):
        joinedEntries = [entry for sublist in joinedEntries.values() for entry in sublist]
        if len(joinedEntries) == 0:
            return None
        return iter(joinedEntries)
    
    def entriesForRegularJoiner(self, isDone, activeClient):
        if not isDone:
            return None
        return activeClient.loadJoinedEntries(self.joinedEntryType())

    def storeJoinedEntries(self, joinedEntries, activeClient):
        match self:
            case JoinerType.ENGLISH:
                return 
            case JoinerType.REGULAR:
                activeClient.storeJoinedEntries(joinedEntries, self.joinedEntryType())

    def entriesToSend(self, joinedEntries, isDone, activeClient): 
        match self:
            case JoinerType.ENGLISH:
                return self.entriesForEnglish(joinedEntries)
            case JoinerType.REGULAR:
                return self.entriesForRegularJoiner(isDone, activeClient)