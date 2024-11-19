import logging
import os
from entryParsing.common.fieldParsing import getClientIdUUID
from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.common.utils import getGamesEntryTypeFromEnv, getHeaderTypeFromEnv, getReviewsEntryTypeFromEnv, maxDataBytes, serializeAndFragmentWithSender, initializeLog
from entryParsing.entry import EntryInterface
from internalCommunication.common.utils import createStrategiesFromNextNodes
from internalCommunication.internalCommunication import InternalCommunication
from .eofController import EofController
import threading
from .activeClient import ActiveClient
from .joinerTypes import JoinerType

PRINT_FREQUENCY = 1000

class Joiner:
    def __init__(self):
        initializeLog()
        self._joinerType = JoinerType(int(os.getenv('JOINER_TYPE')))
        nodeID = os.getenv('NODE_ID')
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'), nodeID)
        self._sendingStrategies = createStrategiesFromNextNodes()
        self._id = int(nodeID)
        self._gamesEntry = getGamesEntryTypeFromEnv()
        self._reviewsEntry = getReviewsEntryTypeFromEnv()
        self._headerType = getHeaderTypeFromEnv()
        self._activeClients = {}
        self._currentClient = None
        self._eofController = EofController(int(nodeID), os.getenv('LISTENING_QUEUE'), int(os.getenv('NODE_COUNT')), self._sendingStrategies)
        self._eofController.execute()
        print("holis")

    def stop(self, _signum, _frame):
        self._internalCommunication.stop()
        
    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def joinReviews(self, reviews: list[EntryInterface]):
        for review in reviews:
            id = review.getAppID()
            name = self._currentClient._games.get(id)
            if name is None:
                continue
            priorJoined =  self._currentClient._joinedEntries.get(id, self._joinerType.defaultEntry(name))
            self._currentClient._joinedEntries[id] = self._joinerType.applyJoining(id, name, priorJoined, review)
    
    def handleReviewsMessage(self, header: HeaderWithTable, data: bytes):
        self._currentClient.updateReviewsTracker(header)
        reviews = self._reviewsEntry.deserialize(data)
        if not self._currentClient._gamesTracker.isDone():
            self._currentClient._unjoinedReviews.extend(reviews)
            return 
        else:
            self.joinReviews(reviews)

    def handleGamesMessage(self, header: HeaderWithTable, data: bytes):
        self._currentClient.updateGamesTracker(header)
        entries = self._gamesEntry.deserialize(data)
        for entry in entries:
            self._currentClient.storeGamesEntry(entry)

    def shouldSendPackets(self, toSend: list[EntryInterface]):
        return (self._currentClient.finishedReceiving() or 
                (not self._currentClient.finishedReceiving() and len(toSend) != 0))

    def _handleSending(self, clientId: bytes):
        currClient = self._currentClient
        toSend, self._currentClient._joinedEntries, self._currentClient._sent = self._joinerType.entriesToSend(joinedEntries=currClient._joinedEntries, 
                                                                                                                isDone=currClient.finishedReceiving(),
                                                                                                                sent=currClient._sent)
        if not self.shouldSendPackets(toSend):
            return
        packets, self._currentClient._fragment = serializeAndFragmentWithSender(maxDataBytes=maxDataBytes(self._headerType), 
                                                 data=toSend,
                                                 clientId=clientId, 
                                                 senderId=self._id,
                                                 fragment=currClient._fragment,
                                                 hasEOF=False)
        for packet in packets:
            self._sendToNext(packet)
        
    def setCurrentClient(self, clientId: bytes):
        self._currentClient = self._activeClients.setdefault(clientId, ActiveClient(getClientIdUUID(clientId)))

    def _sendToNext(self, msg: bytes):
        for strategy in self._sendingStrategies:
            strategy.sendBytes(self._internalCommunication, msg)

    def handleMessage(self, ch, method, _properties, body):
        header, batch = self._headerType.deserialize(body)
        clientId = header.getClient()
        self.setCurrentClient(clientId)

        if header.getFragmentNumber() % PRINT_FREQUENCY == 0:
            logging.info(f'action: received batch from table {header.getTable()} | {header} | result: success')
        if header.isGamesTable():
            if self._currentClient.isGameDuplicate(header):
                ch.basic_ack(delivery_tag = method.delivery_tag)
                return
            self.handleGamesMessage(header, batch)

        if header.isReviewsTable():
            if self._currentClient.isReviewDuplicate(header):
                ch.basic_ack(delivery_tag = method.delivery_tag)
                return
            self.handleReviewsMessage(header, batch)
        
        if self._currentClient.isGamesDone():
            self.joinReviews(self._currentClient._unjoinedReviews)
            self._currentClient._unjoinedReviews = []

        self._handleSending(clientId)
        self._activeClients[clientId] = self._currentClient

        if self._currentClient.finishedReceiving():
            logging.info(f'action: finished receiving data from client {clientId}| result: success')
            packets, self._currentClient._fragment = serializeAndFragmentWithSender(maxDataBytes=maxDataBytes(self._headerType), 
                                                 data=bytes(),
                                                 clientId=clientId, 
                                                 senderId=self._id,
                                                 fragment=self._currentClient._fragment,
                                                 hasEOF=True)
            self._eofController.finishedProcessing(packets[0], clientId, self._internalCommunication)
            self._activeClients.pop(clientId)


        ch.basic_ack(delivery_tag = method.delivery_tag)