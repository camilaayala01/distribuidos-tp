from entryParsing.entryNameReviewCount import EntryNameReviewCount
from sorterTopFinder.common.sorterTopFinder import SorterTopFinder

"""in charge on finding the 90th percentile of negative reviews"""
class SorterActionNegativeReviews(SorterTopFinder):
    def __init__(self):
        super().__init__("SorterActionNegativeReviews", EntryNameReviewCount, None)

    def getBatchTop(self, batch: list[EntryNameReviewCount]) -> list[EntryNameReviewCount]:
        return self._entrySorter.sort(batch, False)
    
    def mustElementGoFirst(self, first: EntryNameReviewCount, other: EntryNameReviewCount):
        return not first.isGreaterThan(other)

    def topHasCapacity(self, mergedList):
        return True

    def updatePartialTop(self, newOrderedList):
        self._partialTop = newOrderedList