import os
from entryParsing.common.header import Header
from entryParsing.entryAppID import EntryAppID
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from grouperReviews.common.grouperReviews import GrouperReviews
from internalCommunication.internalCommunication import InternalCommunication

class GrouperEnglishPositiveReviews(GrouperReviews):
    def __init__(self): 
        self._internalCommunication = InternalCommunication(os.getenv('GROUP_EN_POS_REV'), os.getenv('NODE_ID'))
        super().__init__()
    
    def sendToNextStep(self, header, result):
        self._internalCommunication.sendToEnglishReviewsConsolidator(header + result)