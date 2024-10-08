from typing import Tuple
from entryParsing.common.fieldParsing import deserializeAppID, deserializeGameName, deserializeGenres, serializeAppID, serializeGameName, serializeGenres
from entryParsing.common.utils import getShardingKey
from entryParsing.entryAppIDName import EntryAppIDName
from .entry import EntryInterface

class EntryAppIDNameGenres(EntryInterface):
    def __init__(self, id: str, name: str, genres: str):
        self._id = id
        self._name = name
        self._genres = genres

    def serialize(self) -> bytes:
        idBytes = serializeAppID(self._id)
        nameBytes = serializeGameName(self._name)
        genresBytes = serializeGenres(self._genres)
        return idBytes + nameBytes + genresBytes

    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> Tuple['EntryAppIDNameGenres', int]:
        id, curr = deserializeAppID(curr, data)
        name, curr = deserializeGameName(curr, data)
        genres, curr = deserializeGenres(curr, data)
        return cls(id, name, genres), curr
    
    @classmethod
    def deserialize(cls, data: bytes): 
        curr = 0
        entries = []
        while len(data) > curr:
            try:
                entry, curr = EntryAppIDNameGenres.deserializeEntry(curr, data)
                entries.append(entry)
            except:
                raise Exception("Can't deserialize entry")
        return entries

    def shardBatch(nodeCount: int, result: list['EntryAppIDNameGenres']) -> list[bytes]:
        resultingBatches = [bytes() for _ in range(nodeCount)]
        for entry in result:
            shardResult = getShardingKey(entry._id, nodeCount)
            resultingBatches[shardResult] = resultingBatches[shardResult] + EntryAppIDName(entry._id, entry._name).serialize()
        return resultingBatches

    def getGenres(self) -> str:
        return self._genres