from abc import ABC, abstractmethod
from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface
from internalCommunication.internalCommunication import InternalCommunication
from sendingStrategy.common.nextNode import NextNode

class SendingStrategy(ABC):
    def __init__(self, nextNode: NextNode):
        self._nextNode = nextNode
        
    def getNextNodeName(self):
        return self._nextNode._queueName
    
    @abstractmethod
    def send(self, middleware: InternalCommunication, header: Header, batch: list[EntryInterface]):
        pass