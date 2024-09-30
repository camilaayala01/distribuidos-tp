import os
from entryParsing.common.entryAppID import EntryAppID
from entryParsing.common.entryAppIDReviewCount import EntryAppIDReviewCount
from grouperReviews.common.grouperReviews import GrouperReviews
from internalCommunication.internalComunication import InternalCommunication

class GrouperPositiveReviews(GrouperReviews):
    def __init__(self): 
        super().__init__(os.getenv('GROUP_POS_REV'))

    