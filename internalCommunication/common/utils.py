import os
from internalCommunication.basicSend import BasicSend
from .nextNode import NextNode
from internalCommunication.directSend import DirectSend
from internalCommunication.sendingStrategy import SendingStrategy

def createStrategiesFromNextNodes(nextNodesStr: str = 'NEXT_NODES', nextEntriesStr: str='NEXT_ENTRIES', nextHeadersStr: str='NEXT_HEADERS') -> list[SendingStrategy]:
    nextNodes = NextNode.parseNodes(os.getenv(nextNodesStr), os.getenv(nextEntriesStr) or "", os.getenv(nextHeadersStr) or "")
    strategies = []
    for node in nextNodes:
        strategies.append(getStrategyFromNextNode(node))
    return strategies

def getStrategyFromNextNode(nextNode: NextNode) -> SendingStrategy:
    if nextNode.hasCountAndShardingAttribute():
        return DirectSend(nextNode)
    else:
        return BasicSend(nextNode)