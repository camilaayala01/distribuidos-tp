import os
from grouperReviews.common.grouperReviews import GrouperReviews

class GrouperActionEnglishNegativeReviews(GrouperReviews):
    def __init__(self): 
        super().__init__(os.getenv('GROUP_ENG_NEG_REV'), os.getenv('NODE_ID'))
    
    def sendToNextStep(self, header, result):
        self._internalCommunication.sendToEnglishReviewsJoinerConsolidator(header + result)

    

    