from entryParsing.entrySorterTopFinder import EntrySorterTopFinder
from .common.fieldParsing import deserializeAppID, deserializeCount, deserializeGameName, serializeAppID, serializeCount, serializeGameName

class EntryAppIDNameReviewCount(EntrySorterTopFinder):
    def __init__(self, _appID: str, _name: str, _reviewCount: int):
        super().__init__(_appID=_appID, _name=_name, _reviewCount=_reviewCount)

    def getAppID(self):
        return self._appID
    
    def getName(self):
        return self._name
    
    def getCount(self):
        return self._reviewCount
          
    def addToCount(self, count: int):
        self._reviewCount += count
    
    def getSortingAtribute(self) -> int:
        return self._reviewCount

    def serialize(self) -> bytes:
        appIDBytes = serializeAppID(self._appID)
        nameBytes = serializeGameName(self._name)
        countBytes = serializeCount(self._reviewCount)

        return appIDBytes + nameBytes + countBytes

    def __str__(self):
        return f"EntryAppIDNameReviewCount(appID={self._appID}, name={self._name}, count={self._reviewCount})"

    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> tuple['EntryAppIDNameReviewCount', int]:
        appID, curr = deserializeAppID(curr, data)
        name, curr = deserializeGameName(curr, data)
        reviewCount, curr = deserializeCount(curr, data)

        return cls(appID, name, reviewCount), curr