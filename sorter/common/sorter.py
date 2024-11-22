import logging
import os
import time
from entryParsing.common.fieldParsing import getClientIdUUID
from entryParsing.entrySorterTopFinder import EntrySorterTopFinder
from internalCommunication.common.utils import createStrategiesFromNextNodes
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.utils import getEntryTypeFromEnv, getHeaderTypeFromEnv, initializeLog, nextEntry
from internalCommunication.internalMessageType import InternalMessageType
from .sorterTypes import SorterType
from .activeClient import ActiveClient

PRINT_FREQUENCY=500
DELETE_TIMEOUT = 5
class Sorter:
    def __init__(self):
        initializeLog()
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'), os.getenv('NODE_ID'))
        self._sorterType = SorterType(int(os.getenv('SORTER_TYPE')))
        self._entryType = getEntryTypeFromEnv()
        self._headerType = getHeaderTypeFromEnv()
        self._topAmount = int(os.getenv('TOP_AMOUNT')) if os.getenv('TOP_AMOUNT') is not None else None
        self._sendingStrategies = createStrategiesFromNextNodes()
        self._activeClients = {}
        self._deletedClients = {} # client id: timestamp of the first time flush was seen
        self._currentClient = None

    def stop(self, _signum, _frame):
        self._internalCommunication.stop()
        for client in self._activeClients.values():
            client.destroy()

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def topHasCapacity(self, newElementsAmount: int):
        if self._topAmount is None:
            return True
        return newElementsAmount < self._topAmount

    def getBatchTop(self, batch: list[EntrySorterTopFinder]):
        sortedBatch = self._entryType.sort(batch, True)
        if self._topAmount is None:
            return sortedBatch
        return sortedBatch[:self._topAmount]
            
    def mustElementGoFirst(self, first: EntrySorterTopFinder, other: EntrySorterTopFinder):
        return first.isGreaterThanOrEqual(other)

    def drainTop(self, entriesGenerator, topEntry, savedAmount):
        while self.topHasCapacity(savedAmount) and topEntry is not None:
            self._currentClient.storeEntry(topEntry)
            topEntry = nextEntry(entriesGenerator)
            savedAmount += 1
        return savedAmount

    def drainNewBatch(self, currElement, savedAmount, newBatchTop):
        while currElement < len(newBatchTop) and self.topHasCapacity(savedAmount):
            self._currentClient.storeEntry(newBatchTop[currElement])
            currElement += 1
            savedAmount += 1
        return savedAmount

    def mergeKeepTop(self, batch: list[EntrySorterTopFinder]):
        if len(batch) == 0:
            return
        
        newBatchTop = self.getBatchTop(batch)
        j = 0
        savedAmount = 0

        entriesGen = self._currentClient.loadEntries()
        topEntry = nextEntry(entriesGen)

        while topEntry is not None and j < len(newBatchTop) and self.topHasCapacity(savedAmount):
            if self.mustElementGoFirst(topEntry, newBatchTop[j]):
                self._currentClient.storeEntry(topEntry)
                topEntry = nextEntry(entriesGen)
            else:
                self._currentClient.storeEntry(newBatchTop[j])
                j += 1
            savedAmount += 1
        
        # it could happen that both of them still have elements, but if so its because top does not 
        # have capacity, so it will not save anything either way
        if topEntry is not None:
            savedAmount = self.drainTop(entriesGen, topEntry, savedAmount)
        elif j < len(newBatchTop):
            savedAmount = self.drainNewBatch(j, savedAmount, newBatchTop)
        
        self._currentClient.saveNewTop(savedAmount)

    def _sendToNext(self, generator):
        extraParamsForHeader = self._sorterType.extraParamsForHeader()
        for strategy in self._sendingStrategies:
            strategy.sendFragmenting(self._internalCommunication, self._currentClient.getClientIdBytes(), 1, generator, **extraParamsForHeader)

    def _handleSending(self, clientId: bytes):
        if not self._currentClient.isDone():
            return
        logging.info(f'action: received all required batches | result: success')
        topGenerator, topAmount = self._currentClient.getResults()
        topGenerator = self._sorterType.preprocessPackets(topGenerator, topAmount)
        self._sendToNext(topGenerator)
        client = self._activeClients.pop(clientId)
        client.destroy()
    
    def setCurrentClient(self, clientId: bytes):
        self._currentClient = self._activeClients.setdefault(clientId, 
                                                             ActiveClient(self._sorterType.initializeTracker(clientId), 
                                                                          getClientIdUUID(clientId),
                                                                          self._entryType))
        
    def handleDataMessage(self, channel, tag, body):
        header, batch = self._headerType.deserialize(body)
        if header.getFragmentNumber() % PRINT_FREQUENCY == 0:
            logging.info(f'action: receive batch | {header} | result: success')
        clientId = header.getClient()
        if clientId in self._deletedClients:
            print("received packet from deleted client lol")
            channel.basic_ack(delivery_tag = tag)
            return
        
        self.setCurrentClient(clientId)
        if self._currentClient.isDuplicate(header):
            channel.basic_ack(delivery_tag = tag)
            return
        
        self._currentClient.update(header)
        entries = self._entryType.deserialize(batch)
        self.mergeKeepTop(entries)
        self._activeClients[clientId] = self._currentClient
        self._handleSending(clientId)
        channel.basic_ack(delivery_tag = tag)

    def handleFlushQueuingAndPropagation(self, clientToRemove, tag, channel):
        if clientToRemove in self._deletedClients:
            if time.perf_counter() - self._deletedClients[clientToRemove] > DELETE_TIMEOUT:
                channel.basic_ack(delivery_tag = tag)
                self._deletedClients.pop(clientToRemove, None)
            else: 
                self._internalCommunication.requeuePacket(tag)
        else:
            self._deletedClients[clientToRemove] = time.perf_counter()
            self._internalCommunication.requeuePacket(tag)
            for strategy in self._sendingStrategies:
                strategy.sendFlush(middleware=self._internalCommunication, clientId=clientToRemove)
    
    """
    returns true if it ended flush forever and packet can be safely acked
    returns false if it should requeue it cause timeout is not done
    """
    def handleClientFlush(self, clientToRemove, tag, channel):
        if self._currentClient and clientToRemove == self._currentClient.getClientIdBytes():
            self._currentClient = None

        if clientToRemove in self._activeClients:
            client = self._activeClients.pop(clientToRemove)
            client.destroy()
            
        self.handleFlushQueuingAndPropagation(clientToRemove, tag, channel)

    def handleMessage(self, ch, method, _properties, body):
        msgType, msg = InternalMessageType.deserialize(body)
        match msgType:
            case InternalMessageType.DATA_TRANSFER:
                self.handleDataMessage(channel=ch, tag=method.delivery_tag, body=msg)
            case InternalMessageType.CLIENT_FLUSH:
                self.handleClientFlush(clientToRemove=msg, tag=method.delivery_tag, channel=ch)
       
