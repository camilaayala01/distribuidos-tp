import re
from entryParsing.common.utils import getEntryTypeFromString
from entryParsing.entry import EntryInterface
from sendingStrategy.common.shardingAtribute import ShardingAttribute

class NextNode:
    def __init__(self, queueName: str, entryType: type, nextNodeCount: int = None, shardingAtribute: ShardingAttribute = None):
        self._queueName = queueName
        self._entryType = entryType
        self._count = nextNodeCount
        self._shardingAttribute = shardingAtribute

    @staticmethod
    def getEntryType(entryType: str):
        if not entryType: 
            return None
        return getEntryTypeFromString(entryType)

    def hasCountAndShardingAttribute(self):
        return self._count is not None and self._shardingAttribute is not None
    
    def entryForNextNode(self, entry: EntryInterface):
        return self._entryType.fromAnother(entry)

    @staticmethod
    def createFromList(attributes: list[str], entryType: str):
        if len(attributes) == 1:
            return NextNode(queueName=attributes[0], entryType=NextNode.getEntryType(entryType))
        elif len(attributes) == 3:
            return NextNode(queueName=attributes[0], nextNodeCount=int(attributes[1]), 
                            shardingAtribute=ShardingAttribute(int(attributes[2])),
                            entryType=NextNode.getEntryType(entryType))
        else: 
            raise Exception("Next node attributes must be 1 if no sharding, 3 if sharding is desired")

    # NEXTNODE,NEXTNODECOUNT,SHARDINGATTR;NEXTNODE,NEXTNODECOUNT,SHARDINGATTR etc. 
    # next node count and sharding attributes are optional
    @staticmethod
    def parseNodes(nextNodeStr: str, nextEntries: str) -> list['NextNode']:
        # manually implement to avoid calling split repeatedly
        tokens = re.split(r';', nextEntries)
        nextNodes = []
        currTokens = []
        currTokensIndex = 0
        for i in nextNodeStr:
            if i == ',':
                currTokensIndex += 1
            elif i == ';':
                nextNodes.append(NextNode.createFromList(currTokens, tokens[currTokensIndex] if currTokensIndex < len(tokens) else None))
                currTokens = []
                currTokensIndex = 0
            else:
                if currTokensIndex >= len(currTokens):
                    currTokens.append(i)
                else:
                    currTokens[currTokensIndex] += i
        nextNodes.append(NextNode.createFromList(currTokens, tokens[currTokensIndex] if currTokensIndex < len(tokens) else None))
        return nextNodes
