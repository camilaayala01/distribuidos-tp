from sendingStrategy.common.shardingAtribute import ShardingAttribute

class NextNode:
    def __init__(self, queueName: str, nextNodeCount: int = None, shardingAtribute: ShardingAttribute = None):
        self._queueName = queueName
        self._count = nextNodeCount
        self._shardingAttribute = shardingAtribute

    def hasCountAndShardingAttribute(self):
        return self._count is not None and self._shardingAttribute is not None

    @staticmethod
    def createFromList(attributes: list[str]):
        if len(attributes) == 1:
            return NextNode(attributes[0])
        elif len(attributes) == 3:
            return NextNode(attributes[0], int(attributes[1]), ShardingAttribute(int(attributes[2])))
        else: 
            raise Exception("Next node attributes must be 1 if no sharding, 3 if sharding is desired")

    # NEXTNODE,NEXTNODECOUNT,SHARDINGATTR;NEXTNODE,NEXTNODECOUNT,SHARDINGATTR etc. 
    # next node count and sharding attributes are optional
    @staticmethod
    def parse(nextNodeStr: str) -> list['NextNode']:
        # manually implement to avoid calling split repeatedly
        nextNodes = []
        currTokens = []
        currTokensIndex = 0
        for i in nextNodeStr:
            if i == ',':
                currTokensIndex += 1
            elif i == ';':
                nextNodes.append(NextNode.createFromList(currTokens))
                currTokens = []
                currTokensIndex = 0
            else:
                if currTokensIndex >= len(currTokens):
                    currTokens.append(i)
                else:
                    currTokens[currTokensIndex] += i
        nextNodes.append(NextNode.createFromList(currTokens))
        return nextNodes
