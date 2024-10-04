import os
from entryParsing.common.header import Header
from entryParsing.entryAppID import EntryAppID
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from grouperReviews.common.grouperReviews import GrouperReviews
from internalCommunication.internalCommunication import InternalCommunication

class GrouperNegativeReviews(GrouperReviews):
    def __init__(self): 
        self._internalCommunication = InternalCommunication(os.getenv('GROUP_NEG_REV'), os.getenv('NODE_ID'))
        self._nextNodeCount = os.getenv('JOIN_ACT_NEG_REV_COUNT')

    def sendToNextStep(self, header, result):
        shardedResults = EntryAppIDReviewCount._shardBatch(self._nextNodeCount, result)
        serializedHeader = header.serialize()
        for i in range(self._nextNodeCount):
            msg = serializedHeader + shardedResults[i]
            self._internalCommunication.sendToNegativeReviewsActionGamesJoiner(str(id), msg)