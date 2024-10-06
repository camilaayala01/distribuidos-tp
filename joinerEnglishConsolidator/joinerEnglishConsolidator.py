import os
from entryParsing.common.header import Header
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.common.utils import getShardingKey
from entryParsing.entryAppIDNameReviewCount import EntryAppIDNameReviewCount
from joinerConsolidator.joinerConsolidator import JoinerConsolidator

class JoinerEnglishConsolidator(JoinerConsolidator):
    def __init__(self): 
        super().__init__(type=os.getenv('CONS_JOIN_ENG_NEG_REV'), nextNodeCount=1, 
                        priorNodeCount=os.getenv('JOIN_ENG_COUNT_MORE_REV_COUNT'), entriesType=EntryAppIDNameReviewCount)

    def sendToNextStep(self, id: str, data: bytes):
        self._internalCommunication.sendToEnglishNegativeReviewsCounter(id, data)

    """
    this function avoids resharding, when the prior count and next count are the same, 
    as well as the sharding attribute. in this case sharding is by app ID 
    
    """
    def sendToNextWithSameID(self, header: HeaderWithSender, data: bytes):
        priorID=header.getSenderID() 
        headerSerialized=self.getHeaderSerialized()
        for i in range(self._nextNodeCount):
            if i == priorID:
                self.sendToNextStep(i, headerSerialized + data)
            else:
                # send empty payload so they can keep track of the fragment number
                self.sendToNextStep(i, headerSerialized)

    """
    reshards and distributes
    
    """
    def sendToNextResharding(self, data: bytes):
        entries = self._entriesType.deserialize(data)
        resultingBatches = [bytes() for _ in range(self._nextNodeCount)]
        for entry in entries:
            shardResult = getShardingKey(entry._id, self._nextNodeCount)
            resultingBatches[shardResult] += entry.serialize()

        headerSerialized = self.getHeaderSerialized()
        for i in range(resultingBatches):
            self.sendToNextStep(i, headerSerialized + resultingBatches[i])

    def handleSending(self, header: HeaderWithSender, data: bytes):
        if self._priorNodeCount == self._nextNodeCount:
            self.sendToNextWithSameID(header, data)
        else:
            self.sendToNextResharding(data)