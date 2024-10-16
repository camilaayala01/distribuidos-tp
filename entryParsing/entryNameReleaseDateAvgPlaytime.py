# amount of bytes dedicated to stating the length of the name
from typing import Tuple
from datetime import datetime
from entryParsing.entry import EntryInterface
from entryParsing.common import fieldParsing

class EntryNameReleaseDateAvgPlaytime(EntryInterface):
    def __init__(self, _name: str, _releaseDate: str, _avgPlaytimeForever: int):
        super().__init__(_name=_name, _releaseDate=_releaseDate, _avgPlaytimeForever=_avgPlaytimeForever)

    def serialize(self) -> bytes:
        nameBytes = fieldParsing.serializeGameName(self._name)
        releaseDateBytes = fieldParsing.serializeReleaseDate(self._releaseDate)
        avgPlaytimeForeverBytes = fieldParsing.serializePlaytime(self._avgPlaytimeForever)
        return nameBytes + releaseDateBytes + avgPlaytimeForeverBytes
    
    def deserialize(self) -> bytes:
        pass

    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> Tuple['EntryNameReleaseDateAvgPlaytime', int]:
        name, curr = fieldParsing.deserializeGameName(curr, data)
        releaseDate, curr = fieldParsing.deserializeReleaseDate(curr, data)
        avgPlaytimeForever, curr = fieldParsing.deserializePlaytime(curr, data)
        return cls(_name=name, _releaseDate=releaseDate, _avgPlaytimeForever=avgPlaytimeForever), curr
    
    def getDate(self) -> str:
        return self._releaseDate