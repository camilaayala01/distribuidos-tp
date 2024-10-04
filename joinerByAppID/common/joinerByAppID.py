from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from internalCommunication.internalCommunication import InternalCommunication
from packetTracker.defaultTracker import DefaultTracker

"""For query 5"""
class JoinerByAppIDNegativeReviews:
    def __init__(self, type: str, id: str, nodeCount: int):
        self._internalComunnication = InternalCommunication(type, id)
        self._id = int(id)
        # dict of entry name, review count
        self._joinedEntries = {}
        # get from envfile both nodecount and id
        self._gamesTracker = DefaultTracker(nodeCount, self._id)
        self._reviewsTracker = DefaultTracker(nodeCount, self._id)
        self._unjoinedReviews = []

    def joinReviews(self, reviews: list[EntryAppIDReviewCount]):
        for review in reviews:
            id = review.getAppID()
            if id in self._joinedEntries:
                self._joinedEntries[id] = self._joinedEntries[id].addToCount(review.getCount())

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
            # key: app id, value: EntryNameReviewCount initialized with 0 count
            self._joinedEntries[entry._appID] = EntryNameReviewCount(entry._name, 0)

    def _sendToNextStep(self):
        # has to send header with fragments and his own id, as
        # well as body with name and reviewCount
        # partition results into packets like in sorter
        print("not implemented!")
        self._internalComunnication.sendToNegativeReviewsSorter("message not created")

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
            self._sendToNextStep(self)

        ch.basic_ack(delivery_tag = method.delivery_tag)