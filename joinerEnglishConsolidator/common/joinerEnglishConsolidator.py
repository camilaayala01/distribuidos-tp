import os
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.common.utils import getShardingKey
from entryParsing.entryAppIDNameReviewCount import EntryAppIDNameReviewCount
from joiner.common.joinerConsolidator import JoinerConsolidator
import logging

class JoinerEnglishConsolidator(JoinerConsolidator):
    def __init__(self): 
        super().__init__(type=os.getenv('CONS_JOIN_ENG_NEG_REV'), nextNodeCount=int(os.getenv('JOIN_ENG_COUNT_MORE_REV_COUNT')), 
                        priorNodeCount=int(os.getenv('JOIN_ENG_NEG_REV_COUNT')), entriesType=EntryAppIDNameReviewCount)

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
                self.sendToNextStep(str(i), headerSerialized + data)
            else:
                # send empty payload so they can keep track of the fragment number
                self.sendToNextStep(str(i), headerSerialized)
            logging.info(f'action: send batch to joiner counter with id {i} | {header} | result: success')

    """
    reshards and distributes
    
    """
    def sendToNextResharding(self, header: HeaderWithSender, data: bytes):
        entries = self._entriesType.deserialize(data)
        resultingBatches = [bytes() for _ in range(self._nextNodeCount)]
        for entry in entries:
            shardResult = getShardingKey(entry._id, self._nextNodeCount)
            resultingBatches[shardResult] += entry.serialize()

        headerSerialized = self.getHeaderSerialized()
        for i in range(len(resultingBatches)):
            self.sendToNextStep(str(i), headerSerialized + resultingBatches[i])
            logging.info(f'action: send batch to joiner counter with id {i} | header: {header} | result: success')

    def handleSending(self, header: HeaderWithSender, data: bytes):
        if self._priorNodeCount == self._nextNodeCount:
            self.sendToNextWithSameID(header, data)
        else:
            self.sendToNextResharding(header, data)
        