import os
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from joinerByAppID.common.joinerByAppID import JoinerByAppID

class JoinerActionNegativeReviewsPercentile(JoinerByAppID):
    def __init__(self):
        id = os.getenv('NODE_ID')
        super().__init__(type=os.getenv('JOIN_PERC_NEG_REV'), id=id)
        
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
        return EntryNameReviewCount
    
    def storeGamesEntry(self, entry: EntryAppIDName):
        self._joinedEntries[entry._appID] = EntryNameReviewCount(entry._name, 0)

    def entriesToSend(self)-> list[EntryNameReviewCount]:
        return self._joinedEntries.values()

    def reset(self):
        super().reset()
        self._joinedEntries = {}

    def _sendToNextStep(self, msg: bytes):
        self._internalComunnication.sendToActionPercentileSorterConsolidator(msg)