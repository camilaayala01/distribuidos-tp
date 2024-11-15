from collections import defaultdict
import logging
import os
from entryParsing.common.fieldParsing import getClientIdUUID
from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.common.table import Table
from entryParsing.common.utils import getGamesEntryTypeFromEnv, getHeaderTypeFromEnv, getReviewsEntryTypeFromEnv, maxDataBytes, nextEntry, serializeAndFragmentWithSender, initializeLog
from entryParsing.entry import EntryInterface
from internalCommunication.common.utils import createStrategiesFromNextNodes
from internalCommunication.internalCommunication import InternalCommunication
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
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'), os.getenv('NODE_ID'))
        self._sendingStrategies = createStrategiesFromNextNodes()
        self._id = int(nodeID)
        self._gamesEntry = getGamesEntryTypeFromEnv()
        self._reviewsEntry = getReviewsEntryTypeFromEnv()
        self._headerType = getHeaderTypeFromEnv()
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
        if not len(reviews):
            return
        
        batch = defaultdict(list)
        for entry in reviews:
            batch[entry._appID].append(entry)

        generator = self._currentClient.loadGamesEntries(self._gamesEntry)
        while True:
            if not len(batch):
                break
            game = nextEntry(generator)
            if game is None:
                break
            id = game._appID
            if id in batch:
                reviewsWithID = batch.pop(id)
                for review in reviewsWithID:
                    name = game._name
                    priorJoined = self._currentClient._joinedEntries.get(id, self._joinerType.defaultEntry(name)) #leer
                    self._currentClient._joinedEntries[id] = self._joinerType.applyJoining(id, name, priorJoined, review) #escribe
                    
    def handleReviewsMessage(self, data: bytes):
        reviews = self._reviewsEntry.deserialize(data)
        if not self._currentClient._gamesTracker.isDone():
            self._currentClient.storeUnjoinedReviews(reviews) #write
            return
        self.joinReviews(reviews) #write

    def handleGamesMessage(self, data: bytes):
        entries = self._gamesEntry.deserialize(data)
        self._currentClient.storeGamesEntries(entries)

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
                                                 hasEOF=currClient.finishedReceiving())
        for packet in packets:
            self._sendToNext(packet)
        
    def setCurrentClient(self, clientId: bytes):
        self._currentClient = self._activeClients.setdefault(clientId, ActiveClient(getClientIdUUID(clientId)))

    def _sendToNext(self, msg: bytes):
        for strategy in self._sendingStrategies:
            strategy.sendBytes(self._internalCommunication, msg)
    
    def shouldProcessPending(self):
        return self._accumulatedBatches
    
    def setAccumulatedBatches(self, tag, header, batch):
        if self._accumulatedBatches is None:
            self._accumulatedBatches = AccumulatedBatches(tag, header.getTable(), header.getClient(), batch)

    def processPendingBatches(self):
        table = self._accumulatedBatches.getTable()
        if table == Table.Games:
            self.handleGamesMessage(self._accumulatedBatches)
        if table  == Table.Reviews:
            self.handleReviewsMessage(self._accumulatedBatches)
        self._accumulatedBatches = None
    
    def shouldProcessAccumulated(self):
        return self._accumulatedBatches.accumulatedLen() == PREFETCH_COUNT or self._internalCommunication.isQueueEmpty()
    
    def handleMessage(self, ch, method, _properties, body):
        header, batch = self._headerType.deserialize(body)
        clientId = header.getClient()
        self.setCurrentClient(clientId)

        if self._currentClient.isDuplicate(header):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
            
        self.setAccumulatedBatches(method.delivery_tag, header, batch)
        
        if self._accumulatedBatches.accumulate(header, method.delivery_tag, batch):
            self.processPendingBatches()
            self.setAccumulatedBatches(method.delivery_tag, header, batch)
        self._currentClient.updateTracker(header)

        if header.getFragmentNumber() % PRINT_FREQUENCY == 0:
            logging.info(f'action: received batch from table {header.getTable()} | {header} | result: success')
        
        if not self.shouldProcessAccumulated():
            return
        
        self.processPendingBatches()
        if self._currentClient.isGamesDone():
            self.joinReviews(self._currentClient._unjoinedReviews)
            self._currentClient._unjoinedReviews = []

        self._handleSending(clientId)
        for tag in self._accumulatedBatches._pendingTags:
            ch.basic_ack(delivery_tag = tag)
        
        self._activeClients[clientId] = self._currentClient

        if self._currentClient.finishedReceiving():
            logging.info(f'action: finished receiving data from client {clientId}| result: success')
            self._currentClient.destroy()
            self._activeClients.pop(clientId)

        ch.basic_ack(delivery_tag = method.delivery_tag) #cambiarlo