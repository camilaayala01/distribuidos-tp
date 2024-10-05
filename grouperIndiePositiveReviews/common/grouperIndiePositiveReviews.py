import os
from entryParsing.common.header import Header
from entryParsing.entryAppID import EntryAppID
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from grouperReviews.common.grouperReviews import GrouperReviews
from internalCommunication.internalCommunication import InternalCommunication

class GrouperEnglishPositiveReviews(GrouperReviews):
    def __init__(self): 
        self._internalCommunication = InternalCommunication(os.getenv('GROUP_INDIE_POS_REV'), os.getenv('NODE_ID'))
        super().__init__()
    
    def sendToNextStep(self, header, result):
        shardedResults = EntryAppIDReviewCount._shardBatch(self._nextNodeCount, result)
        serializedHeader = header.serialize()
        for i in range(self._nextNodeCount):
            msg = serializedHeader + shardedResults[i]
            self._internalCommunication.sendToPositive(str(id), msg)

