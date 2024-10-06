from abc import abstractmethod
import os
from entryParsing.entry import EntryInterface
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from joiner.common.joinerByAppID import JoinerByAppID

class JoinerNameCountByAppID(JoinerByAppID):
    def __init__(self, id: str, type: str):
        super().__init__(type=type, id=id)
        
        self._id = int(id)
        # dict of entry name, review count
        self._joinedEntries = {}

    def joinReviews(self, reviews: list[EntryAppIDReviewCount]):
        for review in reviews:
            id = review.getAppID()
            if id in self._joinedEntries:
                self._joinedEntries[id] = self._joinedEntries[id].addToCount(review.getCount())
        
    @classmethod
    def gamesEntryReceivedType(cls):
        return EntryAppIDName
    
    @classmethod
    def reviewsEntryReceivedType(cls):
        return EntryAppIDReviewCount
    
    def storeGamesEntry(self, entry: EntryAppIDName):
        self._joinedEntries[entry._appID] = EntryNameReviewCount(entry._name, 0)

    @abstractmethod
    def entriesToSend(self)-> list[EntryInterface]:
        pass

    def reset(self):
        super().reset()
        self._joinedEntries = {}

    @abstractmethod
    def _sendToNextStep(self, msg: bytes):
        pass