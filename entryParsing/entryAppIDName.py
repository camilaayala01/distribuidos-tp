from entryParsing.entry import EntryInterface
from .common.fieldParsing import  deserializeAppID, deserializeGameName, serializeAppID, serializeGameName
from entryParsing.common.utils import getShardingKey

class EntryAppIDName(EntryInterface):
    def __init__(self, appID: str, name: str):
        self._appID = appID
        self._name = name

    def serialize(self) -> bytes:
        appIDBytes = serializeAppID(self._appID)
        nameBytes = serializeGameName(self._name)
        return appIDBytes + nameBytes

    def __str__(self):
        return f"EntryAppIDName(appID={self._appID}, name={self._name})"
    
    @classmethod
    def header(cls):
        return "appID, name\n"
    
    def csv(self):
        return f'{self._appID}, {self._name}\n'
    
    @classmethod
    def deserialize(cls, data: bytes) -> list['EntryAppIDName']: 
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                appID, curr = deserializeAppID(curr, data)
                name, curr = deserializeGameName(curr, data)
                entries.append(EntryAppIDName(appID, name))
                
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    
    def shardBatch(nodeCount: int, result: list['EntryAppIDName']) -> list[bytes]:
        resultingBatches = [bytes() for _ in range(nodeCount)]
        for entry in result:
            shardResult = getShardingKey(int(entry._appID), nodeCount)
            resultingBatches[shardResult] = resultingBatches[shardResult] + EntryAppIDName(entry._appID, entry._name).serialize()
        return resultingBatches
    