from abc import ABC, abstractmethod
from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface
from internalCommunication.internalCommunication import InternalCommunication
import logging
from entryParsing.common.utils import initializeLog

class Filterer(ABC):
    def __init__(self, entryType: type, headerType: type, type: str, nodeID: str):
        initializeLog()
        self._entryType = entryType
        self._headerType = headerType
        self._internalCommunication = InternalCommunication(type, nodeID)

    @abstractmethod
    def _sendToNext(self, header: Header, filteredEntries: list[EntryInterface]):
        pass

    def stop(self, _signum, _frame):
        self._internalCommunication.stop()

    def handleMessage(self, ch, method, properties, body):
        header, data = self._headerType.deserialize(body)
        logging.info(f'action: received batch | {header} | result: success')
        entries = self._entryType.deserialize(data)
        filteredEntries = self.filterBatch(entries)
        logging.info(f'action: filtering batch | result: success')
        self._sendToNext(header, filteredEntries)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    @classmethod
    @abstractmethod
    def condition(cls, entry: EntryInterface) -> bool:
        pass
    
    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def filterBatch(self, batch: list[EntryInterface]) -> list[EntryInterface]:
        return [entry for entry in batch if self.__class__.condition(entry)]
        # return [self._filterType.getResultingEntry(entry) for entry in batch if self.__class__.condition(entry)]