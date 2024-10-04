from entryParsing.common.utils import maxDataBytes, serializeAndFragmentWithSender
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from joinerByAppID.common.joinerByAppID import JoinerByAppID


class JoinerByAppIDNegativeReviews(JoinerByAppID):
    def __init__(self, type: str, id: str, nodeCount: int):
        #actually should get from env file
        super().__init__(type, id, nodeCount)
        
        self._id = int(id)
        # dict of entry name, review count
        self._joinedEntries = {}
        # get from envfile both nodecount and id

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

    def _handleSending(self):
        packets = serializeAndFragmentWithSender(maxDataBytes(), self._joinedEntries.values(), self._id)
        for pack in packets:
            self._sendToNextStep(pack)
        self.reset()

    def _sendToNextStep(self, msg: bytes):
        self._internalComunnication.sendToNegativeReviewsSorter(msg)