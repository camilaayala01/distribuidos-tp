from entryParsing.common.utils import getShardingKey
from entryParsing.entry import EntryInterface
from .common.fieldParsing import deserializeAppID, deserializeCount, serializeAppID, serializeCount

class EntryAppIDReviewCount(EntryInterface):
    def __init__(self, _appID: str, _reviewCount: int):
        super().__init__(_appID=_appID, _reviewCount=_reviewCount)

    def getAppID(self):
        return self._appID
    
    def getCount(self):
        return self._reviewCount
    
    def addToCount(self, count: int):
        self._reviewCount += count
    
    def serialize(self) -> bytes:
        appIDBytes = serializeAppID(self._appID)
        countBytes = serializeCount(self._reviewCount)

        return appIDBytes + countBytes

    def __str__(self):
        return f"EntryAppIDReviewCount(appID={self._appID}, count={self._reviewCount})"

    @classmethod
    def deserialize(cls, data: bytes): 
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                appID, curr= deserializeAppID(curr, data)
                reviewCount, curr = deserializeCount(curr, data)
                entries.append(EntryAppIDReviewCount(appID, reviewCount))
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries