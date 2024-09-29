import os
from grouperReviews.common.grouperReviews import GrouperReviews

class GrouperPositiveReviews(GrouperReviews):
    def __init__(self): 
        super().__init__(os.getenv('GROUP_NEG_REV'))