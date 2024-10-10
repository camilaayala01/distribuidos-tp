import os
import logging
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from entryParsing.common.headerWithTable import HeaderWithTable
from grouperReviews.common.grouperReviews import GrouperReviews

"""
Entities that count the amount of reviews in a batch that belong to the same game
grouping them by AppID and sending the a response with AppID, ReviewCount
They receive batches of positive reviews only
More than one entity
Query 3
"""

class GrouperIndiePositiveReviews(GrouperReviews):
    def __init__(self): 
        self._nextNodeCount = int(os.getenv('JOIN_INDIE_POS_REV_COUNT'))
        super().__init__(HeaderWithTable, os.getenv('GROUP_INDIE_POS_REV'), os.getenv('NODE_ID'))
    
    def sendToNextStep(self, header, result):
        shardedResults = EntryAppIDReviewCount._shardBatch(self._nextNodeCount, result)
        serializedHeader = header.serialize()
        for i in range(self._nextNodeCount):
            msg = serializedHeader + shardedResults[i]
            self._internalCommunication.sendToIndiePositiveReviewsJoiner(str(i), msg)
            logging.info(f"action: sending batch to indie joiner | joinerID: {i} | result: success")

