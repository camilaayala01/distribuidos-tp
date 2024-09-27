from .entryNameAvgPlaytime import EntryNameAvgPlaytime
from sorterTopFinder.common.sorterTopFinder import SorterTopFinder

TOP_AMOUNT = 10

class SorterByAvgPlaytime(SorterTopFinder):
    def __init__(self, topAmount: int = TOP_AMOUNT): # for testing purposes
        super().__init__("SorterPlaytime", EntryNameAvgPlaytime, topAmount)