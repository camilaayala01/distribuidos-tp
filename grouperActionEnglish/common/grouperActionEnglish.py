import os
from grouperReviews.common.grouperReviews import GrouperReviews
from entryParsing.common.headerWithSender import HeaderWithSender

class GrouperActionEnglishNegativeReviews(GrouperReviews):
    def __init__(self): 
        super().__init__(HeaderWithSender, os.getenv('GROUP_ENG_NEG_REV'), os.getenv('NODE_ID'))
    
    def sendToNextStep(self, header, result):
        print(result)
        serializedHeader = header.serialize()
        for entry in result:
            serializedHeader += entry.serialize()
        self._internalCommunication.sendToEnglishReviewsJoinerConsolidator(serializedHeader)

    

    