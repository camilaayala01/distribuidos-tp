from .entryNameReviewCount import EntryNameReviewCount
from sorterTopFinder.common.sorterTopFinder import SorterTopFinder

TOP_AMOUNT = 5

class SorterIndiePositiveReviews(SorterTopFinder):
    def __init__(self, topAmount: int = TOP_AMOUNT): # for testing purposes
        super().__init__("SorterReviewCount", EntryNameReviewCount, topAmount)