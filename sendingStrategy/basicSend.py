from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface
from internalCommunication.internalCommunication import InternalCommunication
from sendingStrategy.common.nextNode import NextNode
from sendingStrategy.sendingStrategy import SendingStrategy

class BasicSend(SendingStrategy):
    def __init__(self, nextNode: NextNode):
        super().__init__(nextNode)

    def sendBytes(self, middleware: InternalCommunication, msg: bytes):
        middleware.basicSend(self._nextNode._queueName, msg)

    def send(self, middleware: InternalCommunication, header: Header, batch: list[EntryInterface]):
        msg = self._nextNode.headerForNextNode(header).serialize()
        for entry in batch:
            msg += self._nextNode.entryForNextNode(entry).serialize()
        self.sendBytes(middleware, msg)
