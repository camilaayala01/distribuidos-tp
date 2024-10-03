import os
from entryParsing.common.header import Header
from entryParsing.entryAppID import EntryAppID
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from grouperReviews.common.grouperReviews import GrouperReviews
from internalCommunication.internalCommunication import InternalCommunication

class GrouperPositiveReviews(GrouperReviews):
    def __init__(self): 
        self._internalCommunication = InternalCommunication(os.getenv('GROUP_POS_REV'), os.getenv('NODE_ID'))
    
    def handleMessage(self, ch, method, properties, body):
        header, data = Header.deserialize(body)
        entries = EntryAppID.deserialize(data)
        result = super()._applyStep(entries)
        nodeCount = int(os.getenv('JOIN_ACT_POS_REV_COUNT')) 
        shardedResults = EntryAppIDReviewCount._shardBatch(nodeCount, result)
        serializedHeader = header.serialize()
        for i in range(nodeCount):
            msg = serializedHeader + shardedResults[i]
            self._internalCommunication.sendToPositiveReviewsActionGamesJoiner(str(i), msg)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    

    