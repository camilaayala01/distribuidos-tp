import re
from entryParsing.common.header import Header
from entryParsing.common.utils import getEntryTypeFromString, getHeaderTypeFromString
from entryParsing.entry import EntryInterface
from internalCommunication.common.shardingAtribute import ShardingAttribute

class NextNode:
    def __init__(self, queueName: str, entryType: type, headerType: type, nextNodeCount: int = None, shardingAtribute: ShardingAttribute = None):
        self._queueName = queueName
        self._entryType = entryType
        self._headerType = headerType
        self._count = nextNodeCount
        self._shardingAttribute = shardingAtribute

    def __str__(self):
        return f'queueName {self._queueName} | entryType {self._entryType} | headerType: {self._headerType}'
    
    def hasCountAndShardingAttribute(self):
        return self._count is not None and self._shardingAttribute is not None
    
    def entryForNextNode(self, entry: EntryInterface):
        if self._entryType is None:
            return entry
        return self._entryType.fromAnother(entry)
    
    def headerForNextNode(self, header: Header):
        if self._headerType is None:
            return header
        return self._headerType.fromAnother(header)
    
    @staticmethod
    def getEntryType(entryType: str) -> type:
        if not entryType: 
            return None
        return getEntryTypeFromString(entryType)

    @staticmethod
    def getHeaderType(headerType: str) -> type:
        if not headerType: 
            return None
        return getHeaderTypeFromString(headerType)

    @staticmethod
    def createFromList(attributes: list[str], entryType: str = None, headerType: str = None):
        if len(attributes) == 1:
            return NextNode(queueName=attributes[0], 
                            entryType=NextNode.getEntryType(entryType), 
                            headerType=NextNode.getHeaderType(headerType))
        elif len(attributes) == 3:
            return NextNode(queueName=attributes[0], nextNodeCount=int(attributes[1]), 
                            shardingAtribute=ShardingAttribute(int(attributes[2])),
                            entryType=NextNode.getEntryType(entryType),
                            headerType=NextNode.getHeaderType(headerType))
        else: 
            raise Exception("Next node attributes must be 1 if no sharding, 3 if sharding is desired")

    # NEXTNODE,NEXTNODECOUNT,SHARDINGATTR;NEXTNODE,NEXTNODECOUNT,SHARDINGATTR etc. 
    # next node count and sharding attributes are optional
    @staticmethod
    def parseNodes(nextNodeStr: str, nextEntries: str = '', nextHeaders: str = '') -> list['NextNode']:
        # manually implement to avoid calling split repeatedly
        tokensNextEntries = re.split(r';', nextEntries)
        tokensNextHeaders = re.split(r';', nextHeaders)
        nextNodes = []
        currNode = 0 # it is equal to len but prettier to use
        currTokens = []
        currTokensIndex = 0
        for i in nextNodeStr:
            if i == ',':
                currTokensIndex += 1
            elif i == ';':
                nextNodes.append(NextNode.createFromList(currTokens, 
                                                         tokensNextEntries[currNode] if currNode < len(tokensNextEntries) else None,
                                                         tokensNextHeaders[currNode] if currNode < len(tokensNextHeaders) else None))
                currTokens = []
                currNode += 1
                currTokensIndex = 0
            else:
                if currTokensIndex >= len(currTokens):
                    currTokens.append(i)
                else:
                    currTokens[currTokensIndex] += i
        nextNodes.append(NextNode.createFromList(currTokens, 
                                                tokensNextEntries[currNode] if currNode < len(tokensNextEntries) else None,
                                                tokensNextHeaders[currNode] if currNode < len(tokensNextHeaders) else None))
        return nextNodes
