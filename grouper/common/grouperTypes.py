from enum import Enum
from entryParsing.common.header import Header
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.entry import EntryInterface
from entryParsing.entryAppID import EntryAppID
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryAppIDNameReviewCount import EntryAppIDNameReviewCount
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from entryParsing.entryOSCount import EntryOSCount
from entryParsing.entryOSSupport import EntryOSSupport

class GrouperType(Enum):
    OS_COUNT= 0
    APP_ID_COUNT = 1
    APP_ID_NAME_COUNT = 2

    def entryType(self) -> type:
        match self:
            case GrouperType.OS_COUNT:
                return EntryOSSupport
            case GrouperType.APP_ID_COUNT:
                return EntryAppID
            case GrouperType.APP_ID_NAME_COUNT:
                return EntryAppIDName

    def headerType(self) -> type:
        match self:
            case GrouperType.OS_COUNT:
                return Header
            case GrouperType.APP_ID_COUNT:
                return HeaderWithTable
            case GrouperType.APP_ID_NAME_COUNT:
                return HeaderWithSender
            
    def getOSCountResults(self, entries: list[EntryInterface]) -> list[EntryInterface]:
        windowsCount, macCount, linuxCount= 0, 0, 0
        for entry in entries:
            if entry._windows:
                windowsCount += 1
            if entry._mac:
                macCount +=1
            if entry._linux:
                linuxCount +=1
        return [EntryOSCount(windows=windowsCount, mac=macCount, linux=linuxCount, total=len(entries))]
    
    def buildResultingEntry(self, entry: EntryInterface) -> EntryInterface:
        if self == GrouperType.APP_ID_NAME_COUNT:
            return EntryAppIDNameReviewCount(entry._appID, entry._name, 1)
        elif self == GrouperType.APP_ID_COUNT: 
            return EntryAppIDReviewCount(entry._appID, 1)
    
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

    def getResultingHeader(self, header: Header) -> EntryInterface:
        # only to allow easy changes
        return header
            
    