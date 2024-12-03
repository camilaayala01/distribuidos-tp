from entryParsing.headerInterface import HeaderInterface
from entryParsing.messagePart import MessagePartInterface
from internalCommunication.internalCommunication import InternalCommunication
from internalCommunication.common.nextNode import NextNode
from internalCommunication.internalMessageType import InternalMessageType
from internalCommunication.sendingStrategy import SendingStrategy
from entryParsing.common.utils import maxDataBytes

class BasicSend(SendingStrategy):
    def __init__(self, nextNode: NextNode):
        super().__init__(nextNode)

    def sendBytes(self, middleware: InternalCommunication, msg: bytes):
        middleware.basicSend(self._nextNode._queueName, msg)

    def sendDataBytes(self, middleware: InternalCommunication, msg: bytes):
        self.sendBytes(middleware, InternalMessageType.DATA_TRANSFER.serialize() + msg)

    def sendData(self, middleware: InternalCommunication, header: HeaderInterface, batch: list[MessagePartInterface]):
        msg = self._nextNode.headerForNextNode(header).serialize()
        for entry in batch:
            msg += self._nextNode.entryForNextNode(entry).serialize()
        self.sendDataBytes(middleware, msg)

    def sendFragmenting(self, middleware, clientId, fragment, generator, hasEOF: bool = True, **headerExtraArgs):
        headerType = self._nextNode.getHeader()
        entryConverter = self._nextNode.entryForNextNode
        maxBytes = maxDataBytes(headerType)
        currPacket = bytes()

        try: 
            while True:
                entry = next(generator)
                entryBytes = entryConverter(entry).serialize()
                if len(currPacket) + len(entryBytes) <= maxBytes:
                    currPacket += entryBytes
                else:
                    headerBytes = headerType(_clientId=clientId, _fragment=fragment, _eof=False, **headerExtraArgs).serialize()
                    fragment += 1
                    self.sendDataBytes(middleware, headerBytes + currPacket)
                    currPacket = entryBytes
        except StopIteration:
            packet = headerType(_clientId=clientId, _fragment=fragment, _eof=hasEOF, **headerExtraArgs).serialize() + currPacket
            fragment += 1
            self.sendDataBytes(middleware, packet)
        return fragment
    
    def sendFlush(self, middleware, clientId):
        self.sendBytes(middleware, InternalMessageType.CLIENT_FLUSH.serialize() + clientId)