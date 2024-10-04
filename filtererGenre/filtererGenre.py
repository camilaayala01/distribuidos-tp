from abc import ABC, abstractmethod
from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface
from internalCommunication.internalCommunication import InternalCommunication

class FiltererGenre(ABC):
    def __init__(self, entryType: type, headerType: type, type: str, nodeID: str):
        self._entryType = entryType
        self._headerType = headerType
        self._internalCommunication = InternalCommunication(type, nodeID)

    @abstractmethod
    def _sendToNext(self, header: Header, filteredEntries: list[EntryInterface]):
        pass

    def handleMessage(self, ch, method, properties, body):
        header, data = self._headerType.deserialize(body)
        entries = self._entryType.deserialize(data)
        filteredEntries = self.filterBatch(entries)

        self._sendToNext(header, filteredEntries)

    @classmethod
    @abstractmethod
    def condition(cls, entry: EntryInterface) -> bool:
        pass
    
    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def filterBatch(self, batch: list[EntryInterface]) -> list[EntryInterface]:
        return [entry for entry in batch if self.__class__.condition(entry)]