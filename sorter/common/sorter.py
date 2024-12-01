import logging
import os
import csv
import uuid
from entryParsing.common.fieldParsing import getClientIdUUID, serializeBoolean
from entryParsing.entrySorterTopFinder import EntrySorterTopFinder
from eofController.eofController import EofController
from entryParsing.common.utils import getEntryTypeFromEnv, getHeaderTypeFromEnv, nextRow
from internalCommunication.internalMessageType import InternalMessageType
from statefulNode.statefulNode import StatefulNode
from .sorterTypes import SorterType
from .activeClient import ActiveClient

PRINT_FREQUENCY=500
DELETE_TIMEOUT = 5

class Sorter(StatefulNode):
    def __init__(self):
        super().__init__()
        self._sorterType = SorterType(int(os.getenv('SORTER_TYPE')))
        self._entryType = getEntryTypeFromEnv()
        self._headerType = getHeaderTypeFromEnv()
        self.loadActiveClientsFromDisk()
        self._topAmount = int(os.getenv('TOP_AMOUNT')) if os.getenv('TOP_AMOUNT') is not None else None
        if self._sorterType.requireController():
            self._eofController = EofController(int(os.getenv('NODE_ID')), os.getenv('LISTENING_QUEUE'), int(os.getenv('NODE_COUNT')), self._sendingStrategies)
            self._eofController.execute()

    def createTrackerFromRow(self, row):
        return self._sorterType.loadTracker(row)
    
    def createClient(self, _file, clientId, tracker):
        return ActiveClient(clientId, self._entryType, tracker)
   
    def stop(self, _signum, _frame):
        if self._sorterType.requireController():
           self._eofController.terminateProcess(self._internalCommunication)
        super().stop(_signum, _frame)
        
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

    def drainTop(self, entriesGenerator, topEntry, savedAmount, file):
        while self.topHasCapacity(savedAmount) and topEntry is not None:
            self._currentClient.storeEntry(topEntry, file)
            topEntry = nextRow(entriesGenerator)
            savedAmount += 1
        return savedAmount

    def drainNewBatch(self, currElement, savedAmount, newBatchTop, file):
        while currElement < len(newBatchTop) and self.topHasCapacity(savedAmount):
            self._currentClient.storeEntry(newBatchTop[currElement], file)
            currElement += 1
            savedAmount += 1
        return savedAmount

    def mergeKeepTop(self, batch: list[EntrySorterTopFinder]):        
        newBatchTop = self.getBatchTop(batch)
        j = 0
        savedAmount = 0
        
        with open(self._currentClient.storagePath() + '.tmp', 'w+') as file:
            self._currentClient.storeTracker(file) 
            entriesGen = self._currentClient.loadEntries()
            topEntry = nextRow(entriesGen)
            
            while topEntry is not None and j < len(newBatchTop) and self.topHasCapacity(savedAmount):
                if self.mustElementGoFirst(topEntry, newBatchTop[j]):
                    self._currentClient.storeEntry(topEntry, file) 
                    topEntry = nextRow(entriesGen)
                else:
                    self._currentClient.storeEntry(newBatchTop[j], file) 
                    j += 1
                savedAmount += 1
            # it could happen that both of them still have elements, but if so its because top does not 
            # have capacity, so it will not save anything either way
            if topEntry is not None:
                savedAmount = self.drainTop(entriesGen, topEntry, savedAmount, file)
            elif j < len(newBatchTop):
                savedAmount = self.drainNewBatch(j, savedAmount, newBatchTop, file)
            
            return savedAmount
            
    def sendToNext(self, generator):
        extraParamsForHeader = self._sorterType.extraParamsForHeader()
        fragment = 1
        for strategy in self._sendingStrategies:
            fragment = strategy.sendFragmenting(self._internalCommunication, self._currentClient.getClientIdBytes(), 1, generator, not self._sorterType.requireController(), **extraParamsForHeader)
        return fragment

    def handleSending(self, savedAmount):
        clientId = self._currentClient.getClientIdBytes()
        if not self._currentClient.isDone():
            self._activeClients[clientId] = self._currentClient
            return None
        logging.info(f'action: received all required batches for {getClientIdUUID(clientId)} | result: success')
        topGenerator= self._currentClient.getResults()
        topGenerator = self._sorterType.preprocessPackets(topGenerator, savedAmount)
        fragment = self.sendToNext(topGenerator)
        if self._sorterType.requireController():
            self._eofController.finishedProcessing(fragment, clientId, self._internalCommunication)
        return clientId
    
    def setCurrentClient(self, clientId: bytes):
        self._currentClient = self._activeClients.setdefault(clientId, 
                                                             ActiveClient(getClientIdUUID(clientId),
                                                                          self._entryType,
                                                                          self._sorterType.initializeTracker()))
        
    def processDataPacket(self, header, batch, tag, channel):
        clientId = header.getClient()
        self._currentClient.update(header)
        entries = self._entryType.deserialize(batch)
        savedAmount = self.mergeKeepTop(entries)
        clientDeleted = self.handleSending(savedAmount)
        self._currentClient.saveNewTop()
        if clientDeleted:
            self._internalCommunication.basicSend(self._internalCommunication.getQueueName(), InternalMessageType.CLIENT_FLUSH.serialize() + clientId + serializeBoolean(False))
            pass
        channel.basic_ack(delivery_tag = tag)