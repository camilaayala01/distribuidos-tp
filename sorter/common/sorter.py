import logging
import os
import csv
import uuid
from entryParsing.common.fieldParsing import getClientIdUUID
from entryParsing.entrySorterTopFinder import EntrySorterTopFinder
from eofController.eofController import EofController
from entryParsing.common.utils import getEntryTypeFromEnv, getHeaderTypeFromEnv, nextRow
from statefulNode.statefulNode import StatefulNode
from .sorterTypes import SorterType
from .activeClient import ActiveClient

PRINT_FREQUENCY=500
DELETE_TIMEOUT = 5

class Sorter(StatefulNode):
    def __init__(self):
        super().__init__()
        self.loadActiveClientsFromDisk()
        self._currentClient: ActiveClient = None
        self._sorterType = SorterType(int(os.getenv('SORTER_TYPE')))
        self._entryType = getEntryTypeFromEnv()
        self._headerType = getHeaderTypeFromEnv()
        self._topAmount = int(os.getenv('TOP_AMOUNT')) if os.getenv('TOP_AMOUNT') is not None else None
        if self._sorterType.requireController():
            self._eofController = EofController(int(os.getenv('NODE_ID')), os.getenv('LISTENING_QUEUE'), int(os.getenv('NODE_COUNT')), self._sendingStrategies)
            self._eofController.execute()

    def loadActiveClientsFromDisk(self):
        dataDirectory = f"/{os.getenv('LISTENING_QUEUE')}/clientData/"
        if not os.path.exists(dataDirectory) or not os.path.isdir(dataDirectory):
            return
        
        for filename in os.listdir(dataDirectory):
            path = os.path.join(dataDirectory, filename)
            if not os.path.isfile(path): 
                continue
            
            if path.endswith('.tmp'):
                os.remove(path)
                continue
            
            elif path.endswith('.csv'):
                clientIdstr = path.removesuffix('.csv')
                with open(path, 'r') as file:
                    reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
                    packetTrackerRow = nextRow(reader)
                    tracker = self._sorterType.loadTracker(packetTrackerRow)
                    clientUUID = uuid.UUID(clientIdstr)
                    self._activeClients[clientUUID.bytes] = ActiveClient(clientUUID, self._entryType, tracker)
                    
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

    def drainTop(self, entriesGenerator, topEntry, savedAmount):
        while self.topHasCapacity(savedAmount) and topEntry is not None:
            self._currentClient.storeEntry(topEntry)  
            topEntry = nextRow(entriesGenerator)
            savedAmount += 1
        return savedAmount

    def drainNewBatch(self, currElement, savedAmount, newBatchTop):
        while currElement < len(newBatchTop) and self.topHasCapacity(savedAmount):
            self._currentClient.storeEntry(newBatchTop[currElement]) 
            currElement += 1
            savedAmount += 1
        return savedAmount

    def mergeKeepTop(self, batch: list[EntrySorterTopFinder]):
        # open file
        if len(batch) == 0:
            return
        self._currentClient.openFile()
        newBatchTop = self.getBatchTop(batch)
        j = 0
        savedAmount = 0

        entriesGen = self._currentClient.loadEntries()
        topEntry = nextRow(entriesGen)
        
        while topEntry is not None and j < len(newBatchTop) and self.topHasCapacity(savedAmount):
            if self.mustElementGoFirst(topEntry, newBatchTop[j]):
                self._currentClient.storeEntry(topEntry) 
                topEntry = nextRow(entriesGen)
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
        
        self._currentClient.newSavedAmount(savedAmount)
        self._currentClient.closeFile()

    def sendToNext(self, generator):
        extraParamsForHeader = self._sorterType.extraParamsForHeader()
        fragment = 1
        for strategy in self._sendingStrategies:
            fragment = strategy.sendFragmenting(self._internalCommunication, self._currentClient.getClientIdBytes(), 1, generator, not self._sorterType.requireController(), **extraParamsForHeader)
        return fragment

    def handleSending(self, clientId: bytes):
        if not self._currentClient.isDone():
            return
        logging.info(f'action: received all required batches | result: success')
        topGenerator, topAmount = self._currentClient.getResults()
        topGenerator = self._sorterType.preprocessPackets(topGenerator, topAmount)
        fragment = self.sendToNext(topGenerator)
        if self._sorterType.requireController():
            self._eofController.finishedProcessing(fragment, clientId, self._internalCommunication)
        self._activeClients.pop(clientId)
    
    def setCurrentClient(self, clientId: bytes):
        self._currentClient = self._activeClients.setdefault(clientId, 
                                                             ActiveClient(getClientIdUUID(clientId),
                                                                          self._entryType,
                                                                          self._sorterType.initializeTracker()))
        
    def processDataPacket(self, header, batch, tag, channel):
        clientId = header.getClient() 
        self._currentClient.update(header)
        entries = self._entryType.deserialize(batch)
        self.mergeKeepTop(entries)
        self._activeClients[clientId] = self._currentClient
        self.handleSending(clientId)
        self._currentClient.saveNewTop()
        channel.basic_ack(delivery_tag = tag)