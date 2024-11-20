from collections import defaultdict
import logging
import os
from entryParsing.common.fieldParsing import getClientIdUUID
from entryParsing.common.utils import getGamesEntryTypeFromEnv, getHeaderTypeFromEnv, getReviewsEntryTypeFromEnv, maxDataBytes, nextEntry, serializeAndFragmentWithSender, initializeLog
from entryParsing.entry import EntryInterface
from internalCommunication.common.utils import createStrategiesFromNextNodes
from internalCommunication.internalCommunication import InternalCommunication
from .eofController import EofController
from .accumulatedBatches import AccumulatedBatches
from .activeClient import ActiveClient
from .joinerTypes import JoinerType

PRINT_FREQUENCY = 1000
PREFETCH_COUNT = int(os.getenv('PREFETCH_COUNT'))

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
        self._accumulatedBatches = None

    def stop(self, _signum, _frame):
        for client in self._activeClients.values():
            client.destroy()
        self._internalCommunication.stop()
        self._eofController.stop()
        print("me voy gorda")
        
    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def joinReviews(self, reviews: list[EntryInterface]):
        unjoined = list(self._currentClient.loadReviewsEntries(self._reviewsEntry))
        reviews.extend(unjoined)
        if not reviews:
            return
        batch = defaultdict(list)

        for entry in reviews:
            batch[entry._appID].append(entry)

        generator = self._currentClient.loadGamesEntries(self._gamesEntry)
        while True:
            game = nextEntry(generator)
            if game is None or not len(batch):
                break
            id = game._appID
            name = game._name
            if id in batch:
                reviewsWithID = batch.pop(id)
                for review in reviewsWithID:
                    priorJoined =  self._currentClient._joinedEntries.get(id, self._joinerType.defaultEntry(name, id))
                    self._currentClient._joinedEntries[id] = self._joinerType.applyJoining(id, name, priorJoined, review)
        
        self._joinerType.storeJoinedEntries(self._currentClient._joinedEntries, self._currentClient)

    def handleReviewsMessage(self, data: bytes):
        if len(data) == 0 and not self._currentClient.unjoinedReviews():
            return
        reviews = self._reviewsEntry.deserialize(data)
        if not self._currentClient.isGamesDone():
            self._currentClient.storeUnjoinedReviews(reviews)
            return 
        self.joinReviews(reviews) 

    def handleGamesMessage(self, data: bytes):
        if len(data) == 0:
            return
        entries = self._gamesEntry.deserialize(data)
        self._currentClient.storeGamesEntries(entries)

    def shouldSendPackets(self, toSend):
        return (self._currentClient.finishedReceiving() or 
                (not self._currentClient.finishedReceiving() and toSend is not None))

    def _handleSending(self):
        currClient = self._currentClient
        toSend = self._joinerType.entriesToSend(joinedEntries=currClient._joinedEntries, 
                                                isDone=currClient.finishedReceiving(),
                                                activeClient=currClient)
        self._currentClient._joinedEntries = {}
        if not self.shouldSendPackets(toSend):
            return
        self._sendToNext(toSend)

    def _sendToNext(self, generator):
        for strategy in self._sendingStrategies:
            newFragment = strategy.sendFragmenting(self._internalCommunication, 
                                                   self._currentClient.getClientIdBytes(), 
                                                   self._currentClient._fragment, 
                                                   generator, 
                                                   False,
                                                   _sender = self._id)._fragment
        self._currentClient._fragment = newFragment
    
    def setAccumulatedBatches(self, tag, header, batch):
        accumulator = AccumulatedBatches(header.getClient())
        accumulator.accumulate(tag, header, batch)
        self._accumulatedBatches = accumulator

    def processPendingBatches(self):
        self.handleGamesMessage(self._accumulatedBatches.getGamesBatches())
        self.handleReviewsMessage(self._accumulatedBatches.getReviewsBatches())

        self._handleSending()
        
        if self._currentClient.isGamesDone():
            self._currentClient.removeUnjoinedReviews()
        toAck = self._accumulatedBatches.toAck()
        self._activeClients[self._accumulatedBatches.getClient()] = self._currentClient
        self._accumulatedBatches = None
        return toAck
    
    def shouldProcessAccumulated(self):
        return self._accumulatedBatches.accumulatedLen() == PREFETCH_COUNT or self._currentClient.finishedReceiving()

    """keeps the client if there is one, set a new one if there's not"""
    def setCurrentClient(self, clientId: bytes):
        if self._currentClient:
            return
        self._currentClient = self._activeClients.setdefault(clientId, ActiveClient(getClientIdUUID(clientId)))

    """replaces the old client with a new one"""
    def setNewClient(self, clientId: bytes):
        self._currentClient = None
        self.setCurrentClient(clientId)

    def handleMessage(self, ch, method, _properties, body):
        header, batch = self._headerType.deserialize(body)
        clientId = header.getClient()
        self.setCurrentClient(clientId)

        if self._currentClient.isDuplicate(header):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return

        if self._accumulatedBatches is None:
            self.setAccumulatedBatches(method.delivery_tag, header, batch)
        elif not self._accumulatedBatches.accumulate(header=header, tag=method.delivery_tag, batch=batch):
            self._internalCommunication.ackAll(self.processPendingBatches())
            # reset accumulated and set client to correspond to the most recent packet
            self.setAccumulatedBatches(method.delivery_tag, header, batch)
            self.setNewClient(clientId)
            self._currentClient.updateTracker(header)
            return

        if header.getFragmentNumber() % PRINT_FREQUENCY == 0:
            logging.info(f'action: received batch from table {header.getTable()} | {header} | result: success')

        self._currentClient.updateTracker(header)
        if not self.shouldProcessAccumulated():
            return
    
        self._internalCommunication.ackAll(self.processPendingBatches())

        if self._currentClient.finishedReceiving():
            logging.info(f'action: finished receiving data from client {clientId}| result: success')
            packets, self._currentClient._fragment = serializeAndFragmentWithSender(maxDataBytes=maxDataBytes(self._headerType), 
                                                 data=bytes(),
                                                 clientId=clientId, 
                                                 senderId=self._id,
                                                 fragment=self._currentClient._fragment,
                                                 hasEOF=True)
            self._eofController.finishedProcessing(packets[0], clientId, self._internalCommunication)
            self._currentClient.destroy()
            self._activeClients.pop(clientId)

