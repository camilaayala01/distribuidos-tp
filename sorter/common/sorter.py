import logging
import os
from entryParsing.entrySorterTopFinder import EntrySorterTopFinder
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.utils import getEntryTypeFromEnv, getHeaderTypeFromEnv, initializeLog
from sendingStrategy.common.utils import createStrategiesFromNextNodes
from .sorterTypes import SorterType
from .activeClient import ActiveClient

PRINT_FREQUENCY=500

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
        self._currentClient = None

    def stop(self, _signum, _frame):
        self._internalCommunication.stop()

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def mergeKeepTop(self, batch: list[EntrySorterTopFinder]):
        if len(batch) == 0:
            return
        
        newBatchTop = self._sorterType.getBatchTop(batch, self._topAmount, self._entryType)

        i, j = 0, 0
        mergedList = []

        while i < len(self._currentClient._partialTop) and j < len(newBatchTop):
            if self._sorterType.mustElementGoFirst(self._currentClient._partialTop[i], newBatchTop[j]):
                mergedList.append(self._currentClient._partialTop[i])
                i += 1
            else:
                mergedList.append(newBatchTop[j])
                j += 1
        
        if self._sorterType.topHasCapacity(newElementsAmount=len(mergedList), topAmount=self._topAmount):
            # only 1 will have elements
            mergedList.extend(self._currentClient._partialTop[i:])
            mergedList.extend(newBatchTop[j:])

        self._currentClient._partialTop = self._sorterType.updatePartialTop(mergedList, self._topAmount)
        
    def _sendToNext(self, msg: bytes):
        for strategy in self._sendingStrategies:
            strategy.sendBytes(self._internalCommunication, msg)

    def _handleSending(self, clientId: bytes):
        if not self._currentClient.isDone():
            return
        logging.info(f'action: received all required batches | result: success')
        packets = self._sorterType.preprocessPackets(self._currentClient._partialTop)
        data = self._sorterType.serializeAndFragment(clientId, packets, self._headerType)
        for pack in data:
            self._sendToNext(pack)

        self._activeClients.pop(clientId)
    
    def setCurrentClient(self, clientID: bytes):
        self._currentClient = self._activeClients.setdefault(clientID, ActiveClient(self._sorterType.initializeTracker()))
        
    def handleMessage(self, ch, method, properties, body):
        header, batch = self._headerType.deserialize(body)
        if header.getFragmentNumber() % PRINT_FREQUENCY == 0:
            logging.info(f'action: receive batch | {header} | result: success')
        clientId = header.getClient()
        self.setCurrentClient(clientId)
        if self._currentClient.isDuplicate(header):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
        
        self._currentClient.update(header)
        entries = self._entryType.deserialize(batch)
        self.mergeKeepTop(entries)
        self._activeClients[clientId] = self._currentClient
        self._handleSending(clientId)
        ch.basic_ack(delivery_tag = method.delivery_tag)

