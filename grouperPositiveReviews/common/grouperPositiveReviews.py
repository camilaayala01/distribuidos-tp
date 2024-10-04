import os
from entryParsing.common.header import Header
from entryParsing.entryAppID import EntryAppID
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from grouperReviews.common.grouperReviews import GrouperReviews
from internalCommunication.internalCommunication import InternalCommunication

class GrouperPositiveReviews(GrouperReviews):
    def __init__(self): 
        self._internalCommunication = InternalCommunication(os.getenv('GROUP_POS_REV'), os.getenv('NODE_ID'))
        super().__init__(os.getenv('JOIN_ACT_POS_REV_COUNT'))
    
    def sendToNextStep(self, id, msg):
        self._internalCommunication.sendToPositiveReviewsActionGamesJoiner(str(id), msg)

    

    