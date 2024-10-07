import os
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from grouperReviews.common.grouperReviews import GrouperReviews
from entryParsing.common.headerWithTable import HeaderWithTable

class GrouperActionPercentileNegativeReviews(GrouperReviews):
    def __init__(self): 
        self._nextNodeCount = int(os.getenv('JOIN_PERC_NEG_REV_COUNT'))
        super().__init__(headerType=HeaderWithTable, type=os.getenv('GROUP_PERC_NEG_REV'), id=os.getenv('NODE_ID'))

    def sendToNextStep(self, header, result):
        shardedResults = EntryAppIDReviewCount._shardBatch(self._nextNodeCount, result)
        serializedHeader = header.serialize()
        for i in range(self._nextNodeCount):
            msg = serializedHeader + shardedResults[i]
            self._internalCommunication.sendToActionNegativeReviewsJoiner(str(id), msg)