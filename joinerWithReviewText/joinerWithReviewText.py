from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.common.utils import maxDataBytes, serializeAndFragmentWithSender
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryAppIDNameReviewText import EntryAppIDNameReviewText
from entryParsing.entryAppIDReviewText import EntryAppIDReviewText
from joinerByAppID.common.joinerByAppID import JoinerByAppID

class JoinerByAppIDNegativeReviews(JoinerByAppID):
    def __init__(self, type: str, id: str):
        super().__init__(type, id)

        self._joinedEntries = []
        # key: appid, value: name
        self._gamesReceived = {}

    def joinReviews(self, reviews: list[EntryAppIDReviewText]):
        for review in reviews:
            id = review.getAppID()
            name = self._gamesReceived.get(id)
            if name is not None:
                self._joinedEntries.append(EntryAppIDNameReviewText(id, name, review.getReviewText()))

    @classmethod
    def gamesEntryReceivedType(cls):
        return EntryAppIDName
    
    @classmethod
    def reviewsEntryReceivedType(cls):
        return EntryAppIDReviewText
    
    def reset(self):
        super().reset()
        self._joinedEntries = []
        self._gamesReceived = {}

    def storeGamesEntry(self, entry: EntryAppIDName):
        self._gamesReceived[entry._appID] = entry._name

    def _handleSending(self):
        # could be optimized by sending every once in a while
        packets = serializeAndFragmentWithSender(maxDataBytes(), self._joinedEntries.values(), self._id)
        for pack in packets:
            self._sendToNextStep(pack)
        self.reset()

    def entriesToSend(self)-> list[EntryAppIDNameReviewText]:
        return self._joinedEntries
    
    def _sendToNextStep(self, msg: bytes):
        self._internalComunnication.sendToNegativeReviewsSorter(msg)

