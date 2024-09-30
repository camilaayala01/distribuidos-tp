from entryParsing.common.utils import getShardingKey
from .common.fieldParsing import deserializeVariableLenString, deserializeCount, serializeVariableLenString, serializeCount

APP_ID_LEN = 1 
COUNT_LEN = 4

class EntryAppIDReviewCount:
    def __init__(self, appID: str, count: int):
        self._appID =  appID
        self._count = count

    def serialize(self) -> bytes:
        appIDBytes = serializeVariableLenString(self._appID)
        countBytes = serializeCount(self._count)

        return appIDBytes + countBytes

    def __str__(self):
        return f"EntryAppIDReviewCount(appID={self._appID}, count={self._count})"
    
    @staticmethod
    def deserialize(data: bytes): 
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                appID, curr= deserializeVariableLenString(curr, data)
                reviewCount, curr = deserializeCount(curr, data)
                entries.append(EntryAppIDReviewCount(appID, reviewCount))
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    
 
    def _shardBatch(nodeCount: int, result: list['EntryAppIDReviewCount']) -> list[bytes]:
        resultingBatches = [bytes() for _ in range(nodeCount)]
        for entry in result:
            shardResult = getShardingKey(entry._appID, nodeCount)
            resultingBatches[shardResult] =  resultingBatches[shardResult] + entry.serialize()
        return resultingBatches