from abc import ABC, abstractmethod
import logging
from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.common.utils import maxDataBytes, serializeAndFragmentWithSender, initializeLog
from entryParsing.entry import EntryInterface
from internalCommunication.internalCommunication import InternalCommunication
from packetTracker.defaultTracker import DefaultTracker

class JoinerByAppID(ABC):
    def __init__(self, type: str, id: str):
        initializeLog()
        self._internalCommunication = InternalCommunication(type, id)
        self._id = int(id)
        self._gamesTracker = DefaultTracker()
        self._reviewsTracker = DefaultTracker()
        self._unjoinedReviews = []

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    @abstractmethod
    def joinReviews(self, reviews: list[EntryInterface]):
        pass

    @abstractmethod
    def gamesEntryReceivedType(self) -> EntryInterface:
        pass

    @abstractmethod
    def reviewsEntryReceivedType(self) -> EntryInterface:
        pass

    @abstractmethod
    def storeGamesEntry(self, entry: EntryInterface):
        pass

    def finishedReceiving(self):
        return self._gamesTracker.isDone() and self._reviewsTracker.isDone()
    
    def handleReviewsMessage(self, header: HeaderWithTable, data: bytes):
        self._reviewsTracker.update(header)
        reviews = self.reviewsEntryReceivedType().deserialize(data)

        if not self._gamesTracker.isDone():
            self._unjoinedReviews.extend(reviews)
            return
        
        self.joinReviews(reviews)

    def handleGamesMessage(self, header: HeaderWithTable, data: bytes):
        self._gamesTracker.update(header)
        entries = self.gamesEntryReceivedType().deserialize(data)
        for entry in entries:
            # key: app id, value: EntryNameReviewCount initialized with 0 count
            self.storeGamesEntry(entry)

    @abstractmethod
    def entriesToSend(self)-> list[EntryInterface]:
        pass

    def _handleSending(self):
        packets = serializeAndFragmentWithSender(maxDataBytes(HeaderWithSender), self.entriesToSend(), self._id)
        for pack in packets:
            self._sendToNextStep(pack)
        self.reset()

    def reset(self):
        self._gamesTracker.reset()
        self._reviewsTracker.reset()
        self._unjoinedReviews = []

    @abstractmethod
    def _sendToNextStep(self, msg: bytes):
        pass

    def handleMessage(self, ch, method, properties, body):
        header, batch = HeaderWithTable.deserialize(body)
        logging.info(f'action: received batch from table {header.getTable()} | {header} | result: success')
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
            logging.info(f'action: finished receiving data | result: success')
            self.joinReviews(self._unjoinedReviews)
            self._handleSending()

        ch.basic_ack(delivery_tag = method.delivery_tag)