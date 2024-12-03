from abc import ABC, abstractmethod
from entryParsing.headerInterface import HeaderInterface
from entryParsing.messagePart import MessagePartInterface
from internalCommunication.internalCommunication import InternalCommunication
from internalCommunication.common.nextNode import NextNode

class SendingStrategy(ABC):
    def __init__(self, nextNode: NextNode):
        self._nextNode = nextNode
        
    def __str__(self):
        return f"Strategy: {type(self).__name__}, Next node: {self._nextNode}"
    
    @abstractmethod
    def sendData(self, middleware: InternalCommunication, header: HeaderInterface, batch: list[MessagePartInterface]):
        pass

    @abstractmethod
    def sendFlush(self, clientId: bytes):
        pass

    