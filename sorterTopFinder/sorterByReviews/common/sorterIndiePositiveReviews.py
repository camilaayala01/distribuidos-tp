from .entryNameReviewCount import EntryNameReviewCount
from sorterTopFinder.common.sorterTopFinder import SorterTopFinder

TOP_AMOUNT = 5

"""in charge on finding the top 5 indie games with most positive reviews"""
class SorterIndiePositiveReviews(SorterTopFinder):
    def __init__(self, topAmount: int = TOP_AMOUNT): # for testing purposes
        super().__init__("SorterIndiePositiveReviews", EntryNameReviewCount, topAmount)

    def getBatchTop(self, batch: list[EntryNameReviewCount]) -> list[EntryNameReviewCount]:
        sortedBatch = self._entrySorter.sort(batch, True)
        return sortedBatch[:self._topAmount]