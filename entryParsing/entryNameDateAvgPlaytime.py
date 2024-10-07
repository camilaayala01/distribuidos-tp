# amount of bytes dedicated to stating the length of the name
from entryParsing.common import fieldParsing
from entryParsing.common.fieldParsing import *

class EntryNameDateAvgPlaytime():
    def __init__(self, name: str, releaseDate: str, avgPlaytimeForever: int):
        self._name = name
        self._releaseDate = releaseDate
        self._avgPlaytimeForever = avgPlaytimeForever

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
        return cls(name, releaseDate, avgPlaytimeForever), curr
    
    @classmethod
    def deserialize(cls, data: bytes): 
        
        curr = 0
        entries = []
        while len(data) > curr:
            try:
                print(data[curr:])
                entry, curr = EntryNameDateAvgPlaytime.deserializeEntry(curr, data)
                entries.append(entry)
            except:
                print(data)
                raise Exception("Can't deserialize entry")
        return entries


    def getDate(self) -> str:
        return self._releaseDate