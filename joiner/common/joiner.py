import logging
import os
from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.common.utils import getGamesEntryTypeFromEnv, getHeaderTypeFromEnv, getReviewsEntryTypeFromEnv, maxDataBytes, serializeAndFragmentWithSender, initializeLog
from entryParsing.entry import EntryInterface
from internalCommunication.internalCommunication import InternalCommunication
from .joinerTypes import JoinerType
from packetTracker.defaultTracker import DefaultTracker
from sendingStrategy.common.utils import createStrategiesFromNextNodes

PRINT_FREQUENCY = 100

class Joiner:
    def __init__(self):
        initializeLog()
        self._joinerType = JoinerType(int(os.getenv('JOINER_TYPE')))
        nodeID=os.getenv('NODE_ID')
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'), nodeID)
        self._sendingStrategies = createStrategiesFromNextNodes()
        self._id = int(nodeID)
        self._fragment = 1
        self._gamesEntry = getGamesEntryTypeFromEnv()
        self._reviewsEntry = getReviewsEntryTypeFromEnv()
        self._headerType = getHeaderTypeFromEnv()
        self._gamesTracker = DefaultTracker()
        self._reviewsTracker = DefaultTracker()
        self._unjoinedReviews = []
        # key: app id, value: name
        self._games = {}
        self._joinedEntries = {}
        self._sent = set()

    def stop(self, _signum, _frame):
        self._internalCommunication.stop()
        
    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def joinReviews(self, reviews: list[EntryInterface]):
        for review in reviews:
            id = review.getAppID()
            name = self._games.get(id)
            if name is None:
                continue
            priorJoined = self._joinedEntries.get(id, self._joinerType.defaultEntry(name))
            self._joinedEntries[id] = self._joinerType.applyJoining(id, name, priorJoined, review)

    def finishedReceiving(self):
        return self._gamesTracker.isDone() and self._reviewsTracker.isDone()

    def handleReviewsMessage(self, header: HeaderWithTable, data: bytes):
        self._reviewsTracker.update(header)
        reviews = self._reviewsEntry.deserialize(data)
        if not self._gamesTracker.isDone():
            self._unjoinedReviews.extend(reviews)
            return
        
        self.joinReviews(reviews)

    def storeGamesEntry(self, entry: EntryInterface):
        self._games[entry._appID] = entry._name

    def handleGamesMessage(self, header: HeaderWithTable, data: bytes):
        self._gamesTracker.update(header)
        entries = self._gamesEntry.deserialize(data)
        for entry in entries:
            self.storeGamesEntry(entry)

    def shouldSendPackets(self, toSend: list[EntryInterface]):
        return self.finishedReceiving() or (not self.finishedReceiving() and len(toSend) != 0)

    def _handleSending(self):
        toSend, self._joinedEntries, self._sent = self._joinerType.entriesToSend(joinedEntries=self._joinedEntries, 
                                                                                 isDone=self.finishedReceiving(),
                                                                                 sent=self._sent)
        if not self.shouldSendPackets(toSend):
            return
        packets, self._fragment = serializeAndFragmentWithSender(maxDataBytes=maxDataBytes(self._joinerType.headerType()), 
                                                 data=toSend, 
                                                 id=self._id,
                                                 fragment=self._fragment,
                                                 hasEOF=self.finishedReceiving())
        for packet in packets:
            self._sendToNext(packet)

    def reset(self):
        self._gamesTracker.reset()
        self._reviewsTracker.reset()
        self._fragment = 1
        self._unjoinedReviews = []
        self._games = {}

    def _sendToNext(self, msg: bytes):
        for strategy in self._sendingStrategies:
            strategy.sendBytes(self._internalCommunication, msg)

    def handleMessage(self, ch, method, properties, body):
        header, batch = self._headerType.deserialize(body)
        if header.getFragmentNumber() % PRINT_FREQUENCY == 0:
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
        
        if self._gamesTracker.isDone():
            self.joinReviews(self._unjoinedReviews)
            self._unjoinedReviews = []

        self._handleSending() 
        
        if self.finishedReceiving():
            logging.info(f'action: finished receiving data | result: success')
            self.reset()

        ch.basic_ack(delivery_tag = method.delivery_tag)