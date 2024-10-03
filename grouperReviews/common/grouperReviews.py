from entryParsing.entryAppID import EntryAppID
from abc import ABC
import os
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from entryParsing.common.header import Header
from internalCommunication.internalCommunication import InternalCommunication

class GrouperReviews(ABC):
    def _applyStep(self, entries: list['EntryAppID'])-> list['EntryAppIDReviewCount']:
        return self._buildResult(self._count(entries))
    
    def _count(self, entries: list['EntryAppID']) -> dict[str, int]:
        appIDCount = {}
        for entry in entries:
            if not appIDCount.get(entry._appID):
                appIDCount[entry._appID] = 1
            else:
                appIDCount[entry._appID] = appIDCount[entry._appID] + 1
        return appIDCount
    
    def _buildResult(self, appIDCount: dict[str, int]) -> list['EntryAppIDReviewCount']:
        result = []
        for (key, value) in appIDCount.items():
            result.append(EntryAppIDReviewCount(key, value))
        return result
    
    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

   