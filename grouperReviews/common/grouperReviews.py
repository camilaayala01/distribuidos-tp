from entryParsing.entryAppID import EntryAppID
from abc import ABC
import os
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from entryParsing.common.header import Header
from internalCommunication.internalComunication import InternalCommunication

class GrouperReviews(ABC):
    def __init__(self, type: str): 
        self._type = type
        self._internalComunnication = InternalCommunication(self._type, os.getenv('NODE_ID'))

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
    
    def handleMessage(self, ch, method, properties, body):
        header, data = Header.deserialize(body)
        entries = EntryAppID.deserialize(data)
        result = self._applyStep(entries)
        nodeCount = int(os.getenv('JOIN_ACT_POS_REV_COUNT'))
        shardedResults = EntryAppIDReviewCount._shardBatch(nodeCount, result)
        serializedHeader = header.serialize()
        for i in range(nodeCount):
            msg = serializedHeader + shardedResults[i]
            self._internalComunnication.sendToPositiveReviewsActionGamesJoiner(str(i), msg)

    def execute(self):
        self._internalComunnication.defineMessageHandler(self.handleMessage)

   