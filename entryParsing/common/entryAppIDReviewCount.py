from entryParsing.common.utils import getShardingKey
APP_ID_LEN = 1 
COUNT_LEN = 1
class EntryAppIDReviewCount:
    def __init__(self, appID: str, count: int):
        self._appID =  appID
        self._count = count

    def serialize(self) -> bytes:
        appIDBytes = self._appID.encode()
        appIDLenByte = len(appIDBytes).to_bytes(APP_ID_LEN, 'big')
        countByte = self._count.to_bytes(COUNT_LEN,'big')

        return appIDLenByte + appIDBytes + countByte

    def __str__(self):
        return f"EntryAppIDReviewCount(appID={self._appID}, count={self._count})"
    
    @staticmethod
    def deserialize(data: bytes): 
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                appIDLen = int.from_bytes(data[curr:curr+APP_ID_LEN], 'big')
                curr+=APP_ID_LEN
                appID = data[curr:appIDLen+curr].decode()
                curr += appIDLen
                count = int.from_bytes(data[curr:curr+COUNT_LEN], 'big')
                entries.append(EntryAppIDReviewCount(appID,count))
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    
 
    def _shardBatch(nodeCount: int, result: list['EntryAppIDReviewCount']) -> list[bytes]:
        resultingBatches = []
        for i in range(nodeCount):
            resultingBatches[i] = bytes()
        for entry in result:
            shardResult = getShardingKey(entry._appID, nodeCount)
            resultingBatches[shardResult] =  resultingBatches[shardResult] + entry.serialize()
        return resultingBatches

    