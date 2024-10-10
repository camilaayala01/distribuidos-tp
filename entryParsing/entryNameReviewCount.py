
from entryParsing.common.fieldParsing import deserializeCount, deserializeGameName, serializeCount, serializeGameName
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
        nameBytes = serializeGameName(self._name)
        reviewCountBytes = serializeCount(self._reviewCount)

        return nameBytes + reviewCountBytes  
    
    @classmethod
    def header(cls):
        return("Name,positive_score\n")
    
    def csv(self):
        return(f'{self._name},{self._reviewCount}\n')

    def __str__(self):
        return f"{self._name},{self._reviewCount};"

    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> tuple['EntryNameReviewCount', int]:
        name, curr = deserializeGameName(curr, data)
        reviewCount, curr = deserializeCount(curr, data)

        return cls(name, reviewCount), curr
    
    def getSortingAtribute(self) -> int:
        return self._reviewCount

