from abc import ABC, abstractmethod
from entryParsing.common.header import Header
from entryParsing.common.headerWithSender import HeaderWithSender
from internalCommunication.internalCommunication import InternalCommunication
from packetTracker.multiTracker import MultiTracker

class JoinerConsolidator(ABC):
    def __init__(self, type: str, nextNodeCount: int, priorNodeCount: int): 
        self._internalCommunication = InternalCommunication(type, None)
        self._tracker = MultiTracker(priorNodeCount)
        self._nextNodeCount = nextNodeCount
        self._priorNodeCount = priorNodeCount
        self._currFragment = 1

    @abstractmethod
    def sendToNextStep(self, id: str, data: bytes):
        pass
    
    def sendToAll(self, eof: bool, allData: list[bytes]):
        header=Header(fragment=self._currFragment, eof=eof).serialize()
        for i in range(allData):
            msg = header + allData[i]
            self.sendToNextStep(str(id), msg)

    """
    this function avoids resharding, when the prior count and next count are the same, 
    as well as the sharding attribute. in our use case, this second is necessarily true
    
    """
    def sendToSorterWithSameID(self, header: HeaderWithSender, data: bytes):
        if header.isEOF():
            resultingBatches = [bytes() for _ in range(self._nextNodeCount)]
            resultingBatches[HeaderWithSender.getSenderID()] = data
            self.sendToAll(True, resultingBatches)
        else:        
            self.sendToNextStep(self, Header(False, self._currFragment).serialize() + data)
        self._currFragment += 1

    def handleMessage(self, ch, method, properties, body):
        header, data = HeaderWithSender.deserialize(body)
        # handle update and discard duplicates

        if self._priorNodeCount == self._nextNodeCount:
            self.sendToSorterWithSameID(header, data)
        # handle different sharding quantity
        ch.basic_ack(delivery_tag = method.delivery_tag)
