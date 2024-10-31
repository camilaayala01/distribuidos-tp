from enum import Enum
from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface
from entryParsing.entryAppIDNameReviewCount import EntryAppIDNameReviewCount
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from entryParsing.entryOSCount import EntryOSCount

class GrouperType(Enum):
    OS_COUNT= 0
    APP_ID_COUNT = 1
    APP_ID_NAME_COUNT = 2
            
    def getOSCountResults(self, entries: list[EntryInterface]) -> list[EntryInterface]:
        windowsCount, macCount, linuxCount= 0, 0, 0
        for entry in entries:
            if entry._windows:
                windowsCount += 1
            if entry._mac:
                macCount +=1
            if entry._linux:
                linuxCount +=1
        return [EntryOSCount(_windows=windowsCount, _mac=macCount, _linux=linuxCount, _total=len(entries))]
    
    def buildResultingEntry(self, entry: EntryInterface) -> EntryInterface:
        if self == GrouperType.APP_ID_NAME_COUNT:
            return EntryAppIDNameReviewCount.fromAnother(entry, _reviewCount=1)
        elif self == GrouperType.APP_ID_COUNT: 
            return EntryAppIDReviewCount.fromAnother(entry, _reviewCount=1)
    
    def getAppIDCountResults(self, entries: list[EntryInterface]) -> list[EntryInterface]:
        appIDCount = {}
        for entry in entries:
            if entry._appID not in appIDCount:
                appIDCount[entry._appID] = self.buildResultingEntry(entry)
            else:
                appIDCount[entry._appID].addToCount(1)
        
        return list(appIDCount.values())
        
    def getResults(self, entries: list[EntryInterface]) -> list[EntryInterface]:
        match self:
            case GrouperType.OS_COUNT:
                return self.getOSCountResults(entries)
            case GrouperType.APP_ID_COUNT | GrouperType.APP_ID_NAME_COUNT: 
                return self.getAppIDCountResults(entries)
    