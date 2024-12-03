from entryParsing.headerInterface import HeaderInterface
from entryParsing.common.utils import getShardingKey
from entryParsing.messagePart import MessagePartInterface
from internalCommunication.common.shardingAtribute import ShardingAttribute
from internalCommunication.internalCommunication import InternalCommunication
from internalCommunication.internalMessageType import InternalMessageType
from internalCommunication.sendingStrategy import SendingStrategy

class DirectSend(SendingStrategy):
    def __init__(self, nextNode):
        super().__init__(nextNode)

    def sendBytes(self, middleware: InternalCommunication, nodeId: str, msg: bytes):
        middleware.directSend(self._nextNode._queueName, nodeId, msg)

    def sendDataBytes(self, middleware: InternalCommunication, nodeId: str, msg: bytes):
        self.sendBytes(middleware, nodeId, InternalMessageType.DATA_TRANSFER.serialize() + msg)

    def sendData(self, middleware: InternalCommunication, header: HeaderInterface, batch: list[MessagePartInterface]):
        if self._nextNode._shardingAttribute == ShardingAttribute.APP_ID:
            self.shardAndSendByAppID(middleware, header, batch)
        elif self._nextNode._shardingAttribute == ShardingAttribute.FRAGMENT_NUMBER:
            self.shardAndSendByFragmentNumber(middleware, header, batch)
    
    def shardAndSendByFragmentNumber(self, middleware: InternalCommunication, header: HeaderInterface, batch: list[MessagePartInterface]):
        headerSerialized = self._nextNode.headerForNextNode(header).serialize()
        msg = headerSerialized
        for entry in batch:
            msg += self._nextNode.entryForNextNode(entry).serialize()

        shardingKey = header.getFragmentNumber() % self._nextNode._count
        
        if header.isEOF():
            # announce eof to all
            for i in range(self._nextNode._count):
                if shardingKey == i:
                    self.sendDataBytes(middleware, str(i), msg)
                else:
                    self.sendDataBytes(middleware, str(i), headerSerialized)
        else:
            # only send to the corresponding node
            self.sendDataBytes(middleware, str(shardingKey), msg)

    def shardAndSendByAppID(self, middleware: InternalCommunication, header: HeaderInterface, batch: list[MessagePartInterface]):
        resultingBatches = [bytes() for _ in range(self._nextNode._count)]
        for entry in batch:
            routingKey = getShardingKey(entry._appID, self._nextNode._count)
            resultingBatches[routingKey] += self._nextNode.entryForNextNode(entry).serialize()

        serializedHeader = self._nextNode.headerForNextNode(header).serialize()
        for i in range(self._nextNode._count):
            self.sendDataBytes(middleware, str(i), serializedHeader + resultingBatches[i])

    def sendFlush(self, middleware, clientId):
        for i in range(self._nextNode._count):
            self.sendBytes(middleware, str(i), InternalMessageType.CLIENT_FLUSH.serialize() + clientId)