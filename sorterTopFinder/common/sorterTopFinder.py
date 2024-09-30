from abc import ABC, abstractmethod
from entryParsing.entrySorterTopFinder import EntrySorterTopFinder

TOP_AMOUNT = 5

class SorterTopFinder(ABC):
    def __init__(self, type: str, entrySorter: type, topAmount: int):
        self._type = type
        self._entrySorter = entrySorter
        self._partialTop = None
        self._topAmount = topAmount

    def execute(self, data: bytes):
        # communication is not developed
        print("work in progress")

    @abstractmethod
    def getBatchTop(self, batch: list[EntrySorterTopFinder]) -> list[EntrySorterTopFinder]:
        pass

    def topHasCapacity(self, mergedList):
        return len(mergedList) < self._topAmount
        
    def updatePartialTop(self, newOrderedList):
        self._partialTop = newOrderedList[:self._topAmount]

    def mustElementGoFirst(self, first: EntrySorterTopFinder, other: EntrySorterTopFinder):
        return first.isGreaterThan(other)

    def mergeKeepTop(self, batch: list[EntrySorterTopFinder]):
        if len(batch) == 0:
            return
        
        newBatchTop = self.getBatchTop(batch)
        
        if self._partialTop is None:
            self.updatePartialTop(newBatchTop)
            return

        i, j = 0, 0
        mergedList = []

        while i < len(self._partialTop) and j < len(newBatchTop):
            if self.mustElementGoFirst(self._partialTop[i], newBatchTop[j]):
                mergedList.append(self._partialTop[i])
                i += 1
            else:
                mergedList.append(newBatchTop[j])
                j += 1
        
        if self.topHasCapacity(mergedList):
            # only 1 will have elements
            mergedList.extend(self._partialTop[i:])
            mergedList.extend(newBatchTop[j:])

        self.updatePartialTop(mergedList)
            
            
