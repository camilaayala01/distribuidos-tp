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
        match self:
            case JoinerType.ENGLISH:
                priorJoined.append(EntryAppIDNameReviewText(id, name, review.getReviewText()))
            case _:
                priorJoined.addToCount(review.getCount()) 
        return priorJoined

    def entriesForEnglish(self, joinedEntries, sent):
        toSend = []
        newSent = set()
        for id, entries in joinedEntries.items():
            # if it had already reached 5000, or just reached it
            if len(entries) >= REQUIRED_ENTRIES or id in sent:
                newSent.add(id)
                toSend.extend(entries)

        for id in newSent:
            del joinedEntries[id]
            sent.add(id)
            
        return toSend, joinedEntries, sent
    
    def entriesForIndie(self, joinedEntries, isDone):
        if not isDone:
            return [], joinedEntries, set() 
        return joinedEntries.values(), {}, set()

    def entriesForPercentile(self, joinedEntries, isDone):
        entries = []
        if isDone:
            for id, entry in joinedEntries.items():
                entries.append(EntryAppIDNameReviewCount.fromAnother(entry, _appID=id))
            joinedEntries = {}
        return entries, joinedEntries, set()

    # returns a tuple of entries to send, joined entries, sent ids that will be ignored from now on
    def entriesToSend(self, joinedEntries, isDone, sent): 
        match self:
            case JoinerType.ENGLISH:
                return self.entriesForEnglish(joinedEntries, sent)
            case JoinerType.INDIE:
                return self.entriesForIndie(joinedEntries, isDone)
            case JoinerType.PERCENTILE:
                return self.entriesForPercentile(joinedEntries, isDone)
    