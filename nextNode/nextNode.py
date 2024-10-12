from sendingStrategy.directSend import ShardingAttribute

class NextNode:
    def __init__(self, queueName: str, nextNodeCount: str, shardingAtribute: ShardingAttribute = None):
        self._queueName = queueName
        self._nextNodeCount = nextNodeCount
        self._shardingAttribute = shardingAtribute
    
    @staticmethod
    def createFromList(attributes: list[str]):
        if len(attributes) == 2:
            return NextNode(attributes[0], attributes[1])
        elif len(attributes) == 3:
            return NextNode(attributes[0], attributes[1], ShardingAttribute(int(attributes[2])))

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
# NEXTNODE,NEXTNODECOUNT,SHARDINGATTR;NEXTNODE,NEXTNODECOUNT,SHARDINGATTR etc. el sharding attribute es opcional
#nextNodes = GROUPER,2,1;JOINER,3