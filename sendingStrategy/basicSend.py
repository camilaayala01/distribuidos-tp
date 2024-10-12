from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface
from internalCommunication.internalCommunication import InternalCommunication
from sendingStrategy.sendingStrategy import SendingStrategy

class BasicSend(SendingStrategy):
    def __init__(self, queueName):
        self._queueName = queueName

    def send(self, middleware: InternalCommunication, header: Header, batch: list[EntryInterface]):
        msg = header.serialize()
        for entry in batch:
            msg += entry.serialize()
        middleware.basicSend(self._queueName, msg)
