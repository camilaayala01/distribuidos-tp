import os
from entryParsing.common.header import Header
from entryParsing.entryAppID import EntryAppID
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from grouperReviews.common.grouperReviews import GrouperReviews
from internalCommunication.internalCommunication import InternalCommunication

class GrouperNegativeReviews(GrouperReviews):
    def __init__(self): 
        self._internalCommunication = InternalCommunication(os.getenv('GROUP_NEG_REV'), os.getenv('NODE_ID'))

    def handleMessage(self, ch, method, properties, body):
        header, data = Header.deserialize(body)
        result = super()._applyStep(EntryAppID.deserialize(data))
        nodeCount = int(os.getenv('JOIN_ACT_NEG_REV_COUNT')) 
        shardedResults = EntryAppIDReviewCount._shardBatch(nodeCount, result)
        serializedHeader = header.serialize()
        for i in range(nodeCount):
            msg = serializedHeader + shardedResults[i]
            self._internalCommunication.sendToNegativeReviewsActionGamesJoiner(str(i), msg)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)