import os
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from grouperReviews.common.grouperReviews import GrouperReviews

class GrouperIndiePositiveReviews(GrouperReviews):
    def __init__(self): 
        super().__init__(os.getenv('GROUP_INDIE_POS_REV'), os.getenv('NODE_ID'))
    
    def sendToNextStep(self, header, result):
        shardedResults = EntryAppIDReviewCount._shardBatch(self._nextNodeCount, result)
        serializedHeader = header.serialize()
        for i in range(self._nextNodeCount):
            msg = serializedHeader + shardedResults[i]
            self._internalCommunication.sendToIndiePositiveReviewsJoiner(str(id), msg)

