from entryParsing.common.fieldParsing import deserializeGameName, deserializePlaytime, serializeGameName, serializePlaytime
from entryParsing.entrySorterTopFinder import EntrySorterTopFinder

class EntryNameAvgPlaytime(EntrySorterTopFinder):
    def __init__(self, name: str, avgPlaytime: int):
        super().__init__(name)
        self._avgPlaytime = avgPlaytime

    def serialize(self) -> bytes:
        nameBytes = serializeGameName(self._name)
        avgPlaytimeBytes = serializePlaytime(self._avgPlaytime)

        return nameBytes + avgPlaytimeBytes   

    def __str__(self):
        return f"EntryNameAvgPlaytime(name={self._name}, avgPlaytime={self._avgPlaytime})"
    
    def csv(self):
        return f"{self._name}, {self._avgPlaytime}\n"

    @classmethod
    def header(self):
        return f"name, avgPlaytime\n"
    
    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> tuple['EntryNameAvgPlaytime', int]:
        name, curr = deserializeGameName(curr, data)
        avgPlaytime, curr = deserializePlaytime(curr, data)

        return cls(name, avgPlaytime), curr
    
    def getSortingAtribute(self) -> int:
        return self._avgPlaytime
    
    @classmethod
    def sort(cls, entries: list['EntrySorterTopFinder']) -> list['EntrySorterTopFinder']:
        return super().sort(entries, True)