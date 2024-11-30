from entryParsing.entrySorterTopFinder import EntrySorterTopFinder

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