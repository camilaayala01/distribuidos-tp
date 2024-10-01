import os
from entryParsing.entryAppID import EntryAppID
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from grouperReviews.common.grouperReviews import GrouperReviews
from internalCommunication.internalCommunication import InternalCommunication

class GrouperPositiveReviews(GrouperReviews):
    def __init__(self): 
        super().__init__(os.getenv('GROUP_POS_REV'))

    