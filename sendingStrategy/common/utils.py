import os
from sendingStrategy.basicSend import BasicSend
from sendingStrategy.common.nextNode import NextNode
from sendingStrategy.directSend import DirectSend
from sendingStrategy.sendingStrategy import SendingStrategy

def createStrategiesFromNextNodes() -> list[SendingStrategy]:
    nextNodes = NextNode.parse(os.getenv('NEXT_NODES'))
    strategies = []
    for node in nextNodes:
        strategies.append(getStrategyFromNextNode(node))
    return strategies

def getStrategyFromNextNode(nextNode: NextNode) -> SendingStrategy:
    if nextNode.hasCountAndShardingAttribute():
        return DirectSend(nextNode)
    else:
        return BasicSend(nextNode)