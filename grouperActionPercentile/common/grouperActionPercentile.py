import os
import logging
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from grouperReviews.common.grouperReviews import GrouperReviews
from entryParsing.common.headerWithTable import HeaderWithTable

"""
Entities that count the amount of reviews in a batch that belong to the same game
grouping them by AppID and sending a response with App ID and Review Count
They receive batches of negative reviews only
More than one entity
Query 5
"""

class GrouperActionPercentileNegativeReviews(GrouperReviews):
    def __init__(self): 
        self._nextNodeCount = int(os.getenv('JOIN_PERC_NEG_REV_COUNT'))
        super().__init__(headerType=HeaderWithTable, type=os.getenv('GROUP_PERC_NEG_REV'), id=os.getenv('NODE_ID'))

    def sendToNextStep(self, header, result):
        shardedResults = EntryAppIDReviewCount._shardBatch(self._nextNodeCount, result)
        serializedHeader = header.serialize()
        for i in range(self._nextNodeCount):
            msg = serializedHeader + shardedResults[i]
            self._internalCommunication.sendToActionNegativeReviewsJoiner(str(i), msg)
            logging.info(f"action: sending to joiner action percentile with id {i} | result: success")