import math
import os
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.common.utils import maxDataBytes, serializeAndFragmentWithQueryNumber
from entryParsing.entryAppIDNameReviewCount import EntryAppIDNameReviewCount
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from entryParsing.entryAppIDName import EntryAppIDName
from packetTracker.multiTracker import MultiTracker
from sorter.common.sorter import Sorter

PERCENTILE=90
"""
in charge on finding the 90th percentile of negative reviews
it is only one node that needs to find and sort all entries
For query 5
"""
class SorterConsolidatorActionPercentile(Sorter):
    def __init__(self):
        priorNodeCount = os.getenv('JOIN_PERC_NEG_REV_COUNT')
        super().__init__(id=os.getenv('NODE_ID'), type=os.getenv('CONS_SORT_PERC_NEG_REV'), headerType=HeaderWithSender, 
                         entryType=EntryAppIDNameReviewCount, topAmount=None, tracker=MultiTracker(int(priorNodeCount)))

    def _filterByPercentile(self):
        if not self._partialTop:
            return

        index = math.ceil(PERCENTILE / 100 * len(self._partialTop))
        if index >= len(self._partialTop):
            index = len(self._partialTop) - 1

        while index > 0 and self._partialTop[index] == self._partialTop[index-1]:
            index -= 1
        
        self._partialTop=self._partialTop[index:]
    
    def _removeCount(self, entries: list[EntryAppIDNameReviewCount]):
        newEntries = []
        for entry in entries:
            newEntries.append(EntryAppIDName(entry.getAppID(), entry.getName()))
        return newEntries

    def _serializeAndFragment(self):
        self._filterByPercentile()
        entriesWithRemoved = self._removeCount(self._partialTop)
        serializeAndFragmentWithQueryNumber(maxDataBytes(), entriesWithRemoved, 5)

    def getBatchTop(self, batch: list[EntryAppIDNameReviewCount]) -> list[EntryAppIDNameReviewCount]:
        return self._entryType.sort(batch, False)
    
    def mustElementGoFirst(self, first: EntryAppIDNameReviewCount, other: EntryAppIDNameReviewCount):
        return not first.isGreaterThan(other)

    def topHasCapacity(self, mergedList):
        return True

    def updatePartialTop(self, newOrderedList):
        self._partialTop = newOrderedList

    def _sendToNextStep(self, data: bytes):
        self._internalComunnication.sendToDispatcher(data)