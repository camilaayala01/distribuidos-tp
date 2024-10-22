import logging
import os
from entryParsing.entrySorterTopFinder import EntrySorterTopFinder
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.utils import getEntryTypeFromEnv, getHeaderTypeFromEnv, initializeLog
from sendingStrategy.common.utils import createStrategiesFromNextNodes
from .sorterTypes import SorterType

class Sorter:
    def __init__(self):
        initializeLog()
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'), os.getenv('NODE_ID'))
        self._sorterType = SorterType(int(os.getenv('SORTER_TYPE')))
        self._entryType = getEntryTypeFromEnv()
        self._headerType = getHeaderTypeFromEnv()
        self._packetTracker = self._sorterType.initializeTracker()
        self._partialTop = []
        self._topAmount = int(os.getenv('TOP_AMOUNT')) if os.getenv('TOP_AMOUNT') is not None else None
        self._sendingStrategies = createStrategiesFromNextNodes()

    def stop(self, _signum, _frame):
        self._internalCommunication.stop()

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def reset(self):
        self._partialTop = []
        self._packetTracker.reset()
        logging.info(f'action: reseting stored data for next client | result: success')

    def mergeKeepTop(self, batch: list[EntrySorterTopFinder]):
        if len(batch) == 0:
            return
        
        newBatchTop = self._sorterType.getBatchTop(batch, self._topAmount, self._entryType)

        i, j = 0, 0
        mergedList = []

        while i < len(self._partialTop) and j < len(newBatchTop):
            if self._sorterType.mustElementGoFirst(self._partialTop[i], newBatchTop[j]):
                mergedList.append(self._partialTop[i])
                i += 1
            else:
                mergedList.append(newBatchTop[j])
                j += 1
        
        if self._sorterType.topHasCapacity(newElementsAmount=len(mergedList), topAmount=self._topAmount):
            # only 1 will have elements
            mergedList.extend(self._partialTop[i:])
            mergedList.extend(newBatchTop[j:])

        self._partialTop = self._sorterType.updatePartialTop(mergedList, self._topAmount)
        
    def _sendToNext(self, msg: bytes):
        for strategy in self._sendingStrategies:
            strategy.sendBytes(self._internalCommunication, msg)

    def _handleSending(self):
        if not self._packetTracker.isDone():
            return
        logging.info(f'action: received all required batches | result: success')
        packets = self._sorterType.preprocessPackets(self._partialTop)
        data = self._sorterType.serializeAndFragment(packets, self._headerType)
        for pack in data:
            self._sendToNext(pack)
        self.reset()

    def handleMessage(self, ch, method, properties, body):
        header, batch = self._headerType.deserialize(body)
        logging.info(f'action: receive batch | {header} | result: success')
        if self._packetTracker.isDuplicate(header):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
        self._packetTracker.update(header)
        entries = self._entryType.deserialize(batch)
        self.mergeKeepTop(entries)
        self._handleSending()
        ch.basic_ack(delivery_tag = method.delivery_tag)

