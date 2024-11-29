
from entryParsing.common.fieldParsing import deserializeCount, deserializeGameName, serializeCount, serializeGameName
from entryParsing.entrySorterTopFinder import EntrySorterTopFinder

class EntryNameReviewCount(EntrySorterTopFinder):
    def __init__(self, _name: str, _reviewCount: int):
        super().__init__(_name=_name, _reviewCount=_reviewCount)

    def getName(self):
        return self._name
    
    def getCount(self):
        return self._reviewCount
    
    def addToCount(self, count: int):
        self._reviewCount += count

    @classmethod
    def header(cls):
        return("Name,positive_score\n")

    def __str__(self):
        return f"{self._name},{self._reviewCount};"
    
    def getSortingAtribute(self) -> int:
        return self._reviewCount

