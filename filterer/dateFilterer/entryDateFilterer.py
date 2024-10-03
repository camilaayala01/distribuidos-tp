# amount of bytes dedicated to stating the length of the name
from typing import Tuple
from datetime import datetime
NAME_LEN = 1
RELEASE_DATE_LEN = 10
AVG_PLAYTIME_FOREVER_LEN = 4

class EntryDateFilterer():
    def __init__(self, name: str, releaseDate: datetime, avgPlaytimeForever: int):
        self._name = name
        self._releaseDate = releaseDate
        self._avgPlaytimeForever = avgPlaytimeForever

    def serialize(self) -> bytes:
        serialized = bytes()
        nameBytes = self._name.encode()
        serialized += len(nameBytes).to_bytes(NAME_LEN, 'big') + nameBytes
        releaseDateBytes = self._releaseDate.strftime("%Y-%m-%d").encode()
        avgPlaytimeForeverBytes = self._avgPlaytimeForever.to_bytes(AVG_PLAYTIME_FOREVER_LEN, 'big')
        return serialized + releaseDateBytes + avgPlaytimeForeverBytes

    def serializeForQuery2(self) -> bytes:
        serialized = bytes()
        nameBytes = self._name.encode()
        serialized += len(nameBytes).to_bytes(NAME_LEN, 'big') + nameBytes
        avgPlaytimeForeverBytes = self._avgPlaytimeForever.to_bytes(AVG_PLAYTIME_FOREVER_LEN, 'big')
        return serialized + avgPlaytimeForeverBytes
    
    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> Tuple['EntryDateFilterer', int]:
        nameLen = int.from_bytes(data[curr:curr + NAME_LEN], 'big')
        curr += NAME_LEN
        name = data[curr:nameLen + curr].decode()
        curr += nameLen
        releaseDate = datetime.strptime(data[curr:RELEASE_DATE_LEN + curr].decode(), "%Y-%m-%d")
        curr += RELEASE_DATE_LEN
        avgPlaytimeForever = int.from_bytes(data[curr:curr + AVG_PLAYTIME_FOREVER_LEN], 'big')
        curr += AVG_PLAYTIME_FOREVER_LEN

        return cls(name, releaseDate, avgPlaytimeForever), curr
    
    def getDate(self) -> datetime:
        return self._releaseDate