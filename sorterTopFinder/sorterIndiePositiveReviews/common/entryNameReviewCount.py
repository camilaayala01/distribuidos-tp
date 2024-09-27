from typing import Tuple

from sorterTopFinder.common.entrySorterTopFinder import EntrySorterTopFinder

REVIEW_COUNT_LEN = 4

class EntryNameReviewCount(EntrySorterTopFinder):
    def __init__(self, name: str, reviewCount: int):
        super().__init__(name)
        self._reviewCount = reviewCount

    def serialize(self) -> bytes:
        baseSerialized = super().serialize()
        reviewCountBytes = self._reviewCount.to_bytes(REVIEW_COUNT_LEN, 'big')
        
        return baseSerialized + reviewCountBytes  

    def __str__(self):
        return f"EntryNameReviewCount(name={self._name}, reviewCount={self._reviewCount})"
    
    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> Tuple['EntryNameReviewCount', int]:
        curr, name = super().deserializeName(curr, data)
        reviewCount = int.from_bytes(data[curr:curr + REVIEW_COUNT_LEN], 'big')
        curr += REVIEW_COUNT_LEN

        return cls(name, reviewCount), curr
    
    def getSortingAtribute(self) -> int:
        return self._reviewCount
