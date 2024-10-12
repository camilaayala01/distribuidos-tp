from abc import ABC, abstractmethod
from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface
from internalCommunication.internalCommunication import InternalCommunication

class SendingStrategy(ABC):
    @abstractmethod
    def send(self, middleware: InternalCommunication, header: Header, batch: list[EntryInterface]):
        pass