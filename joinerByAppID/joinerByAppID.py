from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from internalCommunication.internalCommunication import InternalCommunication
from packetTracker.defaultTracker import DefaultTracker

class JoinerByAppIDNegativeReviews:
    def __init__(self, type: str, id: str, nodeCount: int):
        self._internalComunnication = InternalCommunication(type, id)
        self._id = int(id)
        self._joinedEntries = {}
        # get from envfile both nodecount and id
        self._gamesTracker = DefaultTracker(nodeCount, self._id)
        self._reviewsTracker = DefaultTracker(nodeCount, self._id)
        self._unjoinedReviews = []

    def joinReviews(self, reviews: list[EntryAppIDReviewCount]):
        for review in reviews:
            id = review.getAppID()
            if id in self._joinedEntries:
                name, count = self._joinedEntries[id]
                self._joinedEntries[id] = (name, count + review.getCount())

    def finishedReceiving(self):
        return self._gamesTracker.isDone() and self._reviewsTracker.isDone()
    
    def handleReviewsMessage(self, header: HeaderWithTable, data: bytes):
        self._reviewsTracker.update(header)
        reviews = EntryAppIDReviewCount.deserialize(data)

        if not self._gamesTracker.isDone():
            self._unjoinedReviews.extend(reviews)
            return
        
        self.joinReviews(reviews)

    def handleGamesMessage(self, header: HeaderWithTable, data: bytes):
        self._gamesTracker.update(header)
        entries = EntryAppIDName.deserialize(data)
        for entry in entries:
            # key: app id, value: (name, count)
            self._joinedEntries[entry._appID] = (entry._name, 0)

        if self.finishedReceiving():
            self.joinReviews(self._unjoinedReviews)

    def _sendToNextStep(self, data: bytes):
        print("not implemented!")

    def handleMessage(self, ch, method, properties, body):
        header, batch = HeaderWithTable.deserialize(body)

        if header.isGamesTable():
            if self._gamesTracker.isDuplicate(header):
                ch.basic_ack(delivery_tag = method.delivery_tag)
                return
            self.handleGamesMessage(header, batch)

        if header.isReviewsTable():
            if self._reviewsTracker.isDuplicate(header):
                ch.basic_ack(delivery_tag = method.delivery_tag)
                return
            self.handleReviewsMessage(header, batch)
        
        if self.finishedReceiving():
            self.joinReviews(self._unjoinedReviews)


        ch.basic_ack(delivery_tag = method.delivery_tag)