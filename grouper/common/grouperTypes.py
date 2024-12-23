from enum import Enum
from entryParsing.messagePart import MessagePartInterface
from entryParsing.reducedEntries import EntryAppIDNameReviewCount, EntryAppIDReviewCount, EntryOSCount

class GrouperType(Enum):
    OS_COUNT= 0
    APP_ID_COUNT = 1
    APP_ID_NAME_COUNT = 2
            
    def getOSCountResults(self, entries: list[MessagePartInterface]) -> list[MessagePartInterface]:
        windowsCount, macCount, linuxCount= 0, 0, 0
        for entry in entries:
            if entry._windows:
                windowsCount += 1
            if entry._mac:
                macCount +=1
            if entry._linux:
                linuxCount +=1
        return [EntryOSCount(_windowsCount=windowsCount, _macCount=macCount, _linuxCount=linuxCount, _totalCount=len(entries))]
    
    def buildResultingEntry(self, entry: MessagePartInterface) -> MessagePartInterface:
        if self == GrouperType.APP_ID_NAME_COUNT:
            return EntryAppIDNameReviewCount.fromAnother(entry, _reviewCount=1)
        elif self == GrouperType.APP_ID_COUNT: 
            return EntryAppIDReviewCount.fromAnother(entry, _reviewCount=1)
    
    def getAppIDCountResults(self, entries: list[MessagePartInterface]) -> list[MessagePartInterface]:
        appIDCount = {}
        for entry in entries:
            if entry._appID not in appIDCount:
                appIDCount[entry._appID] = self.buildResultingEntry(entry)
            else:
                appIDCount[entry._appID].addToCount(1)
        
        return list(appIDCount.values())
        
    def getResults(self, entries: list[MessagePartInterface]) -> list[MessagePartInterface]:
        match self:
            case GrouperType.OS_COUNT:
                return self.getOSCountResults(entries)
            case GrouperType.APP_ID_COUNT | GrouperType.APP_ID_NAME_COUNT: 
                return self.getAppIDCountResults(entries)
    