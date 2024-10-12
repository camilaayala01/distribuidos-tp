import os
from sendingStrategy.common.nextNode import NextNode
from sendingStrategy.sendingStrategy import SendingStrategy

def createStrategiesFromNextNodes() -> list[SendingStrategy]:
    nextNodes = NextNode.parse(os.getenv('NEXT_NODES'))
    strategies = []
    for node in nextNodes:
        strategies.append(node.getCorrespondingStrategy())
    return strategies