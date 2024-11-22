from collections import defaultdict
import logging
import os
import time
from entryParsing.common.fieldParsing import getClientIdUUID
from entryParsing.common.utils import getGamesEntryTypeFromEnv, getHeaderTypeFromEnv, getReviewsEntryTypeFromEnv, nextEntry, initializeLog
from entryParsing.entry import EntryInterface
from internalCommunication.common.utils import createStrategiesFromNextNodes
from internalCommunication.internalCommunication import InternalCommunication
from internalCommunication.internalMessageType import InternalMessageType
from .accumulatedBatches import AccumulatedBatches
from .activeClient import ActiveClient
from .joinerTypes import JoinerType

PRINT_FREQUENCY = 1000
PREFETCH_COUNT = int(os.getenv('PREFETCH_COUNT'))
DELETE_TIMEOUT = 5

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
        self._deletedClients = {} # client id: timestamp of the first time flush was seen
        self._activeClients = {}
        self._currentClient = None
        self._accumulatedBatches = None

    def stop(self, _signum, _frame):
        for client in self._activeClients.values():
            client.destroy()
        self._internalCommunication.stop()
        
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
                                                   self._currentClient.finishedReceiving(),
                                                   _sender = self._id)
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
   
    def handleFlushQueuingAndPropagation(self, clientToRemove, tag, channel):
        if clientToRemove in self._deletedClients:
            if time.perf_counter() - self._deletedClients[clientToRemove] > DELETE_TIMEOUT:
                channel.basic_ack(delivery_tag = tag)
                self._deletedClients.pop(clientToRemove, None)
                print("finished flush")
            else: 
                self._internalCommunication.requeuePacket(tag)
        else:
            print(f"registering deleted client {clientToRemove}")
            self._deletedClients[clientToRemove] = time.perf_counter()
            self._internalCommunication.requeuePacket(tag)
            for strategy in self._sendingStrategies:
                strategy.sendFlush(middleware=self._internalCommunication, clientId=clientToRemove)
    
    """
    returns true if it ended flush forever and packet can be safely acked
    returns false if it should requeue it cause timeout is not done
    """
    # TODO stop copy pasting this flush
    def handleClientFlush(self, clientToRemove, tag, channel):
        if self._currentClient and clientToRemove == self._currentClient.getClientIdBytes():
            self._currentClient = None
        
        if self._accumulatedBatches and clientToRemove == self._accumulatedBatches.getClient():
            self._internalCommunication.ackAll(self._accumulatedBatches.toAck())
        self._accumulatedBatches = None

        if clientToRemove in self._activeClients:
            client = self._activeClients.pop(clientToRemove)
            client.destroy()
            
        self.handleFlushQueuingAndPropagation(clientToRemove, tag, channel)
           
    def handleDataMessage(self, channel, tag, body):
        header, batch = self._headerType.deserialize(body)
        clientId = header.getClient()
        if clientId in self._deletedClients:
            print("received packet from deleted client lol")
            channel.basic_ack(delivery_tag=tag)
            return
        self.setCurrentClient(clientId)
        
        if self._currentClient.isDuplicate(header):
            channel.basic_ack(delivery_tag=tag)
            return

        if self._accumulatedBatches is None:
            self.setAccumulatedBatches(tag, header, batch)
        elif not self._accumulatedBatches.accumulate(header=header, tag=tag, batch=batch):
            self._internalCommunication.ackAll(self.processPendingBatches())
            # reset accumulated and set client to correspond to the most recent packet
            self.setAccumulatedBatches(tag, header, batch)
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
            self._currentClient.destroy()
            self._activeClients.pop(clientId)

    def handleMessage(self, ch, method, _properties, body):
        msgType, msg = InternalMessageType.deserialize(body)
        match msgType:
            case InternalMessageType.DATA_TRANSFER:
                self.handleDataMessage(channel=ch, tag=method.delivery_tag, body=msg)
            case InternalMessageType.CLIENT_FLUSH:
                self.handleClientFlush(clientToRemove=msg, tag=method.delivery_tag, channel=ch)