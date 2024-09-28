# amount of bytes dedicated to stating the length of the name
from typing import Tuple
from sorterTopFinder.common.entrySorterTopFinder import EntrySorterTopFinder

AVG_PLAYTIME_LEN = 4

class EntryNameAvgPlaytime(EntrySorterTopFinder):
    def __init__(self, name: str, avgPlaytime: int):
        super().__init__(name)
        self._avgPlaytime = avgPlaytime

    def serialize(self) -> bytes:
        baseSerialized = super().serialize()
        avgPlaytimeBytes = self._avgPlaytime.to_bytes(AVG_PLAYTIME_LEN, 'big')

        return baseSerialized + avgPlaytimeBytes   

    def __str__(self):
        return f"EntryNameAvgPlaytime(name={self._name}, avgPlaytime={self._avgPlaytime})"
    
    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> Tuple['EntryNameAvgPlaytime', int]:
        curr, name = super().deserializeName(curr, data)
        reviewCount = int.from_bytes(data[curr:curr + AVG_PLAYTIME_LEN], 'big')
        curr += AVG_PLAYTIME_LEN

        return cls(name, reviewCount), curr
    
    def getSortingAtribute(self) -> int:
        return self._avgPlaytime
    
    @classmethod
    def sort(cls, entries: list['EntrySorterTopFinder']) -> list['EntrySorterTopFinder']:
        return super().sort(entries, True)