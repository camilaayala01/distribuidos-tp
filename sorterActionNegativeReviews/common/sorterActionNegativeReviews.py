from entryParsing.entryNameReviewCount import EntryNameReviewCount
from sorterTopFinder.common.sorterTopFinder import SorterTopFinder

# change to a call to env file or somewhere that stores this
AMOUNT_OF_SORTERS = 2
CORRESPONDING_MODULE = 0

"""in charge on finding the 90th percentile of negative reviews"""
class SorterActionNegativeReviews(SorterTopFinder):
    def __init__(self):
        super().__init__(CORRESPONDING_MODULE, AMOUNT_OF_SORTERS, "SorterActionNegativeReviews", EntryNameReviewCount, None)

    def getBatchTop(self, batch: list[EntryNameReviewCount]) -> list[EntryNameReviewCount]:
        return self._entrySorter.sort(batch, False)
    
    def mustElementGoFirst(self, first: EntryNameReviewCount, other: EntryNameReviewCount):
        return not first.isGreaterThan(other)

    def topHasCapacity(self, mergedList):
        return True

    def updatePartialTop(self, newOrderedList):
        self._partialTop = newOrderedList