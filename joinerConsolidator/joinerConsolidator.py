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

    def reset(self):
        self._tracker.reset()
        self._currFragment = 1

    """
    this function avoids resharding, when the prior count and next count are the same, 
    as well as the sharding attribute. in our use case, this second is necessarily true
    
    """
    def sendToSorterWithSameID(self, header: HeaderWithSender, data: bytes):
        priorID=header.getSenderID() 
        headerSerialized=Header(fragment=self._currFragment, eof=header.isEOF()).serialize()
        for i in range(self._nextNodeCount):
            if i == HeaderWithSender.getSenderID():
                self.sendToNextStep(str(priorID), headerSerialized + data)
            else:
                # send empty header so they can keep track of the fragment number
                self.sendToNextStep(str(priorID), headerSerialized)

        self._currFragment += 1

    def handleMessage(self, ch, method, properties, body):
        header, data = HeaderWithSender.deserialize(body)

        if self._tracker.isDuplicate(header):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
        
        self._tracker.update(header)
        if self._priorNodeCount == self._nextNodeCount:
            self.sendToSorterWithSameID(header, data)

        # handle different sharding quantity
        ch.basic_ack(delivery_tag = method.delivery_tag)
