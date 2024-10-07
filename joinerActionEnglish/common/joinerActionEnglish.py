import os
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.common.utils import maxDataBytes, serializeAndFragmentWithSender
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryAppIDNameReviewText import EntryAppIDNameReviewText
from entryParsing.entryAppIDReviewText import EntryAppIDReviewText
from joiner.common.joinerByAppID import JoinerByAppID

"""
Entities that join all entries maintaining all negative reviews with its text
More than one entity
Query 5
"""
class JoinerActionNegativeReviewsEnglish(JoinerByAppID):
    def __init__(self):
        super().__init__(type=os.getenv('JOIN_ENG_NEG_REV'), id=os.getenv('NODE_ID'), header=HeaderWithSender)
        self._joinedEntries = []
        # key: appid, value: name
        self._gamesReceived = {}

    def joinReviews(self, reviews: list[EntryAppIDReviewText]):
        for review in reviews:
            id = review.getAppID()
            name = self._gamesReceived.get(id)
            if name is not None:
                self._joinedEntries.append(EntryAppIDNameReviewText(id, name, review.getReviewText()))

    def gamesEntryReceivedType(self):
        return EntryAppIDName
    
    def reviewsEntryReceivedType(self):
        return EntryAppIDReviewText
    
    def reset(self):
        super().reset()
        self._joinedEntries = []
        self._gamesReceived = {}

    def storeGamesEntry(self, entry: EntryAppIDName):
        self._gamesReceived[entry._appID] = entry._name

    def _handleSending(self):
        # could be optimized by sending every once in a while
        packets = serializeAndFragmentWithSender(maxDataBytes(self._headerType), self._joinedEntries.values(), self._id)
        for pack in packets:
            self._sendToNextStep(pack)
        self.reset()

    def entriesToSend(self)-> list[EntryAppIDNameReviewText]:
        return self._joinedEntries
    
    def _sendToNextStep(self, msg: bytes):
        self._internalCommunication.sendToEnglishFilter(msg)

