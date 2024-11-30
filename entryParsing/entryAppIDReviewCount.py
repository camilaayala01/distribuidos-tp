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