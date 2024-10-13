from entryParsing.common.header import Header
from entryParsing.common.utils import getShardingKey
from entryParsing.entry import EntryInterface
from internalCommunication.internalCommunication import InternalCommunication
from sendingStrategy.common.shardingAtribute import ShardingAttribute
from sendingStrategy.sendingStrategy import SendingStrategy

class DirectSend(SendingStrategy):
    def __init__(self, nextNode):
        self._nextNode = nextNode

    def getNextNodeName(self):
        return self._nextNode._nextNodeName
    
    def send(self, middleware: InternalCommunication, header: Header, batch: list[EntryInterface]):
        self.shardAndSend(middleware, header, batch)
    
    def shardByFragmentNumber(self, middleware: InternalCommunication, header: Header, batch: list[EntryInterface]):
        msg = header.serialize()
        for entry in batch:
            msg += entry.serialize()

        shardingKey = header.getFragmentNumber() % self._nextNode._nextNodeCount
        
        if header.isEOF():
            # announce eof to all
            for i in range(self._nextNode._nextNodeCount):
                if shardingKey == i:
                    middleware.directSend(self._nextNode._queueName, str(i), msg)
                else:
                    middleware.directSend(self._nextNode._queueName, str(i), header.serialize())
        else:
            # only send to the corresponding node
            middleware.directSend(self._nextNode._queueName, str(shardingKey), msg)

    def shardAndSendByAppID(self, middleware: InternalCommunication, header: Header, batch: list[EntryInterface]):
        resultingBatches = [bytes() for _ in range(self._nextNode._nextNodeCount)]
        for entry in batch:
            routingKey = getShardingKey(entry._appID, self._nextNode._nextNodeCount)
            resultingBatches[routingKey] += entry.serialize()

        serializedHeader = header.serialize()
        for i in range(self._nextNodeCount):
            middleware.directSend(self._nextNode._queueName, str(i), serializedHeader + resultingBatches[i])

    def shardAndSend(self, middleware: InternalCommunication, header: Header, batch: list[EntryInterface]):
        if self._nextNode._shardingAttribute == ShardingAttribute.APP_ID:
            self.shardAndSendByAppID(middleware, header, batch)
        elif self._nextNode._shardingAttribute == ShardingAttribute.FRAGMENT_NUMBER:
            self.shardByFragmentNumber(middleware, header, batch)