import os
from grouperReviews.common.grouperReviews import GrouperReviews
from entryParsing.common.headerWithTable import HeaderWithSender

class GrouperActionEnglishNegativeReviews(GrouperReviews):
    def __init__(self): 
        super().__init__(HeaderWithSender, os.getenv('GROUP_ENG_NEG_REV'), os.getenv('NODE_ID'))
    
    def sendToNextStep(self, header, result):
        self._internalCommunication.sendToEnglishReviewsJoinerConsolidator(header + result)

    

    