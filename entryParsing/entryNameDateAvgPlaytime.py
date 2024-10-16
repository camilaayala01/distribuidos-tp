# amount of bytes dedicated to stating the length of the name
from entryParsing.common import fieldParsing
from entryParsing.common.fieldParsing import *
from entryParsing.entry import EntryInterface

class EntryNameDateAvgPlaytime(EntryInterface):
    def __init__(self, _name: str, _releaseDate: str, _avgPlaytimeForever: int):
        super().__init__(_name=_name, _releaseDate=_releaseDate, _avgPlaytimeForever=_avgPlaytimeForever)

    def serialize(self) -> bytes:
        nameBytes = fieldParsing.serializeGameName(self._name)
        releaseDateBytes = fieldParsing.serializeReleaseDate(self._releaseDate)
        avgPlaytimeForeverBytes = fieldParsing.serializePlaytime(self._avgPlaytimeForever)
        return nameBytes + releaseDateBytes + avgPlaytimeForeverBytes
        
    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> tuple['EntryNameDateAvgPlaytime', int]:
        name, curr = fieldParsing.deserializeGameName(curr, data)
        releaseDate, curr = fieldParsing.deserializeReleaseDate(curr, data)
        avgPlaytimeForever, curr = fieldParsing.deserializePlaytime(curr, data)
        return cls(_name=name, _releaseDate=releaseDate, _avgPlaytimeForever=avgPlaytimeForever), curr
    
    @classmethod
    def deserialize(cls, data: bytes): 
        
        curr = 0
        entries = []
        while len(data) > curr:
            try:
                entry, curr = EntryNameDateAvgPlaytime.deserializeEntry(curr, data)
                entries.append(entry)
            except:
                raise Exception("Can't deserialize entry")
        return entries


    def getDate(self) -> str:
        return self._releaseDate