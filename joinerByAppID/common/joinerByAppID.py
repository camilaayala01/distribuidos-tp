from abc import ABC, abstractmethod
from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.common.utils import maxDataBytes, serializeAndFragmentWithSender
from entryParsing.entry import EntryInterface
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from internalCommunication.internalCommunication import InternalCommunication
from packetTracker.defaultTracker import DefaultTracker

"""For query 5"""
class JoinerByAppID(ABC):
    def __init__(self, type: str, id: str, nodeCount: int):
        self._internalComunnication = InternalCommunication(type, id)
        self._id = int(id)
        self._gamesTracker = DefaultTracker(nodeCount, self._id)
        self._reviewsTracker = DefaultTracker(nodeCount, self._id)
        self._unjoinedReviews = []

    @abstractmethod
    def joinReviews(self, reviews: list[EntryInterface]):
        pass

    @classmethod
    @abstractmethod
    def gamesEntryReceivedType(cls) -> EntryInterface:
        pass

    @classmethod
    @abstractmethod
    def reviewsEntryReceivedType(cls) -> EntryInterface:
        pass

    @abstractmethod
    def storeGamesEntry(self, entry: EntryInterface):
        pass

    def finishedReceiving(self):
        return self._gamesTracker.isDone() and self._reviewsTracker.isDone()
    
    def handleReviewsMessage(self, header: HeaderWithTable, data: bytes):
        self._reviewsTracker.update(header)
        reviews = JoinerByAppID.gamesEntryReceivedType().deserialize(data)

        if not self._gamesTracker.isDone():
            self._unjoinedReviews.extend(reviews)
            return
        
        self.joinReviews(reviews)

    def handleGamesMessage(self, header: HeaderWithTable, data: bytes):
        self._gamesTracker.update(header)
        entries = JoinerByAppID.gamesEntryReceivedType().deserialize(data)
        for entry in entries:
            # key: app id, value: EntryNameReviewCount initialized with 0 count
            self.storeGamesEntry(entry)

    @abstractmethod
    def entriesToSend(self)-> list[EntryInterface]:
        pass

    def _handleSending(self):
        packets = serializeAndFragmentWithSender(maxDataBytes(), self.entriesToSend(), self._id)
        for pack in packets:
            self._sendToNextStep(pack)
        self.reset()

    @abstractmethod
    def _sendToNextStep(self, msg: bytes):
        pass

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
            self._handleSending()

        ch.basic_ack(delivery_tag = method.delivery_tag)