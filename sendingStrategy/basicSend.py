from entryParsing.common.header import Header
from entryParsing.common.headerInterface import HeaderInterface
from entryParsing.entry import EntryInterface
from internalCommunication.internalCommunication import InternalCommunication
from sendingStrategy.common.nextNode import NextNode
from sendingStrategy.sendingStrategy import SendingStrategy
from entryParsing.common.utils import maxDataBytes

class BasicSend(SendingStrategy):
    def __init__(self, nextNode: NextNode):
        super().__init__(nextNode)

    def sendBytes(self, middleware: InternalCommunication, msg: bytes):
        middleware.basicSend(self._nextNode._queueName, msg)

    def send(self, middleware: InternalCommunication, header: HeaderInterface, batch: list[EntryInterface]):
        msg = self._nextNode.headerForNextNode(header).serialize()
        for entry in batch:
            msg += self._nextNode.entryForNextNode(entry).serialize()
        self.sendBytes(middleware, msg)

    def sendFragmenting(self, middleware, clientId, fragment, generator, **headerExtraArgs):
        headerType = self._nextNode.getHeader()
        maxBytes = maxDataBytes(headerType)
        currPacket = bytes()
        try: 
            while True:
                entry = next(generator)
                entryBytes = entry.serialize()
                if len(currPacket) + len(entryBytes) <= maxBytes:
                    currPacket += entryBytes
                else:
                    headerBytes = headerType(_clientId=clientId, _fragment=fragment, _eof=False, **headerExtraArgs).serialize()
                    fragment += 1
                    self.sendBytes(middleware, headerBytes + currPacket)
                    currPacket = entryBytes
        except StopIteration:
            packet = headerType(_clientId=clientId, _fragment=fragment, _eof=True, **headerExtraArgs).serialize() + currPacket
            self.sendBytes(middleware, packet)
