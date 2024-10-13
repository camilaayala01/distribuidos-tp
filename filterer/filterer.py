import os
from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface
from filterer.common.filtererTypes import FiltererType
from internalCommunication.internalCommunication import InternalCommunication
import logging
from entryParsing.common.utils import initializeLog
from sendingStrategy.common.utils import createStrategiesFromNextNodes
from sendingStrategy.sendingStrategy import SendingStrategy

class Filterer:
    def __init__(self):
        initializeLog()
        self._filtererType = FiltererType(int(os.getenv('FILTERER_TYPE')))
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'))
        self._sendingStrategies = createStrategiesFromNextNodes()

    def _sendToNext(self, header: Header, batch: list[EntryInterface]):
        for strategy in self._sendingStrategies:
            newBatch = [self._filtererType.getResultingEntry(entry, strategy.getNextNodeName()) for entry in batch]
            newHeader = self._filtererType.getResultingHeader(header, strategy.getNextNodeName())
            strategy.send(self._internalCommunication, newHeader, newBatch)

    def stop(self, _signum, _frame):
        self._internalCommunication.stop()

    def handleMessage(self, ch, method, properties, body):
        header, data = self._filtererType.headerType().deserialize(body)
        logging.info(f'action: received batch | {header} | result: success')
        entries = self._filtererType.entryType().deserialize(data)
        filteredEntries = self.filterBatch(entries)
        logging.info(f'action: filtering batch | result: success')
        self._sendToNext(header, filteredEntries)
        ch.basic_ack(delivery_tag = method.delivery_tag)
    
    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def filterBatch(self, batch: list[EntryInterface]) -> list[EntryInterface]:
        return [entry for entry in batch if self._filtererType.executeCondition(entry)]