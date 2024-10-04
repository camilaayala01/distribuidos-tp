from typing import Tuple

from entryParsing.common.fieldParsing import deserializeCount, deserializeVariableLenString, serializeCount, serializeVariableLenString
from entryParsing.entrySorterTopFinder import EntrySorterTopFinder

class EntryNameReviewCount(EntrySorterTopFinder):
    def __init__(self, name: str, reviewCount: int):
        super().__init__(name)
        self._reviewCount = reviewCount

    def getName(self):
        return self._name
    
    def getCount(self):
        return self._reviewCount
    
    def addToCount(self, count: int):
        self._reviewCount += count

    def serialize(self) -> bytes:
        nameBytes = serializeVariableLenString(self._name)
        reviewCountBytes = serializeCount(self._reviewCount)

        return nameBytes + reviewCountBytes  

    def __str__(self):
        return f"EntryNameReviewCount(name={self._name}, reviewCount={self._reviewCount})"

    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> Tuple['EntryNameReviewCount', int]:
        name, curr = deserializeVariableLenString(curr, data)
        reviewCount, curr = deserializeCount(curr, data)

        return cls(name, reviewCount), curr
    
    def getSortingAtribute(self) -> int:
        return self._reviewCount

