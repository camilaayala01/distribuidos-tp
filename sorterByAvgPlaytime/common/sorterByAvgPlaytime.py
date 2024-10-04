import os
from entryParsing.entryNameAvgPlaytime import EntryNameAvgPlaytime
from sorterTopFinder.common.sorterTopFinder import SorterTopFinder

TOP_AMOUNT = 10

# change to a call to env file or somewhere that stores this
AMOUNT_OF_SORTERS = 2
CORRESPONDING_MODULE = 0

class SorterByAvgPlaytime(SorterTopFinder):
    def __init__(self, topAmount: int = TOP_AMOUNT): # for testing purposes
        super().__init__(CORRESPONDING_MODULE, AMOUNT_OF_SORTERS, os.getenv('SORT_AVG_PT'), EntryNameAvgPlaytime, topAmount)

    def getBatchTop(self, batch: list[EntryNameAvgPlaytime]) -> list[EntryNameAvgPlaytime]:
        sortedBatch = self._entrySorter.sort(batch)
        return sortedBatch[:self._topAmount]
    
    def _sendToNextStep(self, data: bytes):
        print("sorter joiner for this node is not yet implemented")
        # self._internalComunnication.sendToPositiveReviewsActionGamesJoiner(str(i), msg)