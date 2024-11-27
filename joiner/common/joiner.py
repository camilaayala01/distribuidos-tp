from collections import defaultdict
import logging
import os
from entryParsing.common.fieldParsing import getClientIdUUID
from entryParsing.common.utils import getGamesEntryTypeFromEnv, getHeaderTypeFromEnv, getReviewsEntryTypeFromEnv, nextEntry
from entryParsing.entry import EntryInterface
from eofController.eofController import EofController
from statefulNode.statefulNode import StatefulNode
from .accumulatedBatches import AccumulatedBatches
from .activeClient import ActiveClient
from .joinerTypes import JoinerType
from statefulNode.statefulNode import StatefulNode
PRINT_FREQUENCY = 1000
PREFETCH_COUNT = int(os.getenv('PREFETCH_COUNT'))


class Joiner(StatefulNode):
    def __init__(self):
        super().__init__()
        self._joinerType = JoinerType(int(os.getenv('JOINER_TYPE')))
        self._gamesEntry = getGamesEntryTypeFromEnv()
        self._reviewsEntry = getReviewsEntryTypeFromEnv()
        self._headerType = getHeaderTypeFromEnv()
        nodeID = os.getenv('NODE_ID')
        self._id = int(nodeID)
        self._eofController = EofController(self._id, os.getenv('LISTENING_QUEUE'), int(os.getenv('NODE_COUNT')), self._sendingStrategies)
        self._eofController.execute()
        self._accumulatedBatches = None

    def stop(self, _signum, _frame):
        for client in self._activeClients.values():
            client.destroy()
        self._eofController.terminateProcess(self._internalCommunication)
        self._internalCommunication.stop()
        
    """keeps the client if there is one, set a new one if there's not"""
    def setCurrentClient(self, clientId: bytes):
        if self._currentClient:
            return
        self._currentClient = self._activeClients.setdefault(clientId, ActiveClient(getClientIdUUID(clientId)))
    
    """replaces the old client with a new one"""
    def setNewClient(self, clientId: bytes):
        self._currentClient = None
        self.setCurrentClient(clientId)

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
    
    def handleSending(self):
        currClient = self._currentClient
        toSend = self._joinerType.entriesToSend(joinedEntries=currClient._joinedEntries, 
                                                isDone=currClient.finishedReceiving(),
                                                activeClient=currClient)
        self._currentClient._joinedEntries = {}
        if not self.shouldSendPackets(toSend):
            return
        self.sendToNext(toSend)

    def sendToNext(self, generator):
        for strategy in self._sendingStrategies:
            newFragment = strategy.sendFragmenting(self._internalCommunication, 
                                                   self._currentClient.getClientIdBytes(), 
                                                   self._currentClient._fragment, 
                                                   generator, 
                                                   False,
                                                   _sender = self._id)
        self._currentClient._fragment = newFragment
    
    def setAccumulatedBatches(self, tag, header, batch):
        accumulator = AccumulatedBatches(header.getClient())
        accumulator.accumulate(tag, header, batch)
        self._accumulatedBatches = accumulator

    def processPendingBatches(self):
        self.handleGamesMessage(self._accumulatedBatches.getGamesBatches())
        self.handleReviewsMessage(self._accumulatedBatches.getReviewsBatches())

        self.handleSending()
        
        if self._currentClient.isGamesDone():
            self._currentClient.removeUnjoinedReviews()

        toAck = self._accumulatedBatches.toAck()
        self._activeClients[self._accumulatedBatches._clientId] = self._currentClient
        self._accumulatedBatches = None
        return toAck
    
    def shouldProcessAccumulated(self):
        return self._accumulatedBatches.accumulatedLen() == PREFETCH_COUNT or self._currentClient.finishedReceiving()
    
    def deleteAccumulated(self, clientToRemove):        
        if self._accumulatedBatches and clientToRemove == self._accumulatedBatches.getClient():
            self._internalCommunication.ackAll(self._accumulatedBatches.toAck())
            self._accumulatedBatches = None
           
    def processDataPacket(self, header, batch, tag, channel):
        clientId = header.getClient()
        if self._accumulatedBatches is None:
            self.setAccumulatedBatches(tag, header, batch)
        elif not self._accumulatedBatches.accumulate(header=header, tag=tag, batch=batch):
            self._internalCommunication.ackAll(self.processPendingBatches())
            # reset accumulated and set client to correspond to the most recent packet
            self.setAccumulatedBatches(tag, header, batch)
            self.setNewClient(clientId)

        self._currentClient.updateTracker(header)

        if not self.shouldProcessAccumulated():
            self._activeClients[self._accumulatedBatches.getClient()] = self._currentClient
            return

        self._internalCommunication.ackAll(self.processPendingBatches())

        if self._currentClient.finishedReceiving():
            logging.info(f'action: finished receiving data from client {getClientIdUUID(clientId)}| result: success')
            self._eofController.finishedProcessing(self._currentClient._fragment, clientId, self._internalCommunication)
            self._currentClient.destroy()
            self._currentClient = None
            self._activeClients.pop(clientId)

