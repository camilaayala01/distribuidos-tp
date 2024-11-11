from entryParsing.common.headerInterface import HeaderInterface
from entryParsing.common.utils import getShardingKey
from entryParsing.entry import EntryInterface
from internalCommunication.common.shardingAtribute import ShardingAttribute
from internalCommunication.internalCommunication import InternalCommunication
from internalCommunication.sendingStrategy import SendingStrategy

class DirectSend(SendingStrategy):
    def __init__(self, nextNode):
        super().__init__(nextNode)

    def send(self, middleware: InternalCommunication, header: HeaderInterface, batch: list[EntryInterface]):
        self.shardAndSend(middleware, header, batch)
    
    def shardByFragmentNumber(self, middleware: InternalCommunication, header: HeaderInterface, batch: list[EntryInterface]):
        headerSerialized = self._nextNode.headerForNextNode(header).serialize()
        msg = headerSerialized
        for entry in batch:
            msg += self._nextNode.entryForNextNode(entry).serialize()

        shardingKey = header.getFragmentNumber() % self._nextNode._count
        
        if header.isEOF():
            # announce eof to all
            for i in range(self._nextNode._count):
                if shardingKey == i:
                    middleware.directSend(self._nextNode._queueName, str(i), msg)
                else:
                    middleware.directSend(self._nextNode._queueName, str(i), headerSerialized)
        else:
            # only send to the corresponding node
            middleware.directSend(self._nextNode._queueName, str(shardingKey), msg)

    def shardAndSendByAppID(self, middleware: InternalCommunication, header: HeaderInterface, batch: list[EntryInterface]):
        resultingBatches = [bytes() for _ in range(self._nextNode._count)]
        for entry in batch:
            routingKey = getShardingKey(entry._appID, self._nextNode._count)
            resultingBatches[routingKey] += self._nextNode.entryForNextNode(entry).serialize()

        serializedHeader = self._nextNode.headerForNextNode(header).serialize()
        for i in range(self._nextNode._count):
            middleware.directSend(self._nextNode._queueName, str(i), serializedHeader + resultingBatches[i])

    def shardAndSend(self, middleware: InternalCommunication, header: HeaderInterface, batch: list[EntryInterface]):
        if self._nextNode._shardingAttribute == ShardingAttribute.APP_ID:
            self.shardAndSendByAppID(middleware, header, batch)
        elif self._nextNode._shardingAttribute == ShardingAttribute.FRAGMENT_NUMBER:
            self.shardByFragmentNumber(middleware, header, batch)