from entryParsing.common.entryAppID import EntryAppID
from abc import ABC

from entryParsing.common.entryAppIDReviewCount import EntryAppIDReviewCount
from internalCommunication.internalComunication import InternalCommunication

class GrouperReviews(ABC):
    def __init__(self, type: str): 
        self._type = type
        self._internalComunnication = InternalCommunication(self._type)

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
        for key, value in appIDCount:
            result.append(EntryAppIDReviewCount(key, value))
        return result
    
    def handleMessage(self, ch, method, properties, body):
        entries = EntryAppID.deserialize(body)
        result = self._applyStep(entries)
        shardedResults = EntryAppIDReviewCount._shardBatch(result)
        for shardingKey in len(shardedResults):
            self._internalComunnication.sendToPositiveReviewsActionGamesJoiner(shardingKey, shardedResults[shardingKey])

    def execute(self):
        self._internalComunnication.defineMessageHandler(self.handleMessage)

   