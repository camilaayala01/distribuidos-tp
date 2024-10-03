import os
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from sorterTopFinder.common.sorterTopFinder import SorterTopFinder

TOP_AMOUNT = 5

# change to a call to env file or somewhere that stores this
AMOUNT_OF_SORTERS = 2
CORRESPONDING_MODULE = 0

"""in charge on finding the top 5 indie games with most positive reviews"""
class SorterIndiePositiveReviews(SorterTopFinder):
    def __init__(self, topAmount: int = TOP_AMOUNT): # for testing purposes
        super().__init__(CORRESPONDING_MODULE, AMOUNT_OF_SORTERS, os.getenv('SORT_INDIE_POS_REV'), EntryNameReviewCount, topAmount)

    def getBatchTop(self, batch: list[EntryNameReviewCount]) -> list[EntryNameReviewCount]:
        sortedBatch = self._entrySorter.sort(batch, True)
        return sortedBatch[:self._topAmount]
    
    def _sendToNextStep(self, data: bytes):
        print("sorter joiner for this node is not yet implemented")
        # self._internalComunnication.sendToPositiveReviewsActionGamesJoiner(str(i), msg)