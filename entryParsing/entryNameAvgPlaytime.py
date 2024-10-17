from entryParsing.common.fieldParsing import deserializeGameName, deserializePlaytime, serializeGameName, serializePlaytime
from entryParsing.entrySorterTopFinder import EntrySorterTopFinder

class EntryNameAvgPlaytime(EntrySorterTopFinder):
    def __init__(self, _name: str, _avgPlaytime: int):
        super().__init__(_name=_name, _avgPlaytime=_avgPlaytime)

    def serialize(self) -> bytes:
        nameBytes = serializeGameName(self._name)
        avgPlaytimeBytes = serializePlaytime(self._avgPlaytime)

        return nameBytes + avgPlaytimeBytes   

    def __str__(self):
        return f"{self._name},{self._avgPlaytime};"
    
    def csv(self):
        return f"{self._name},{self._avgPlaytime}\n"

    @classmethod
    def header(self):
        return f"Name,Average playtime forever\n"
    
    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> tuple['EntryNameAvgPlaytime', int]:
        name, curr = deserializeGameName(curr, data)
        avgPlaytime, curr = deserializePlaytime(curr, data)

        return cls(name, avgPlaytime), curr
    
    def getSortingAtribute(self) -> int:
        return self._avgPlaytime
    
    @classmethod
    def sort(cls, entries: list['EntrySorterTopFinder'], reversed: bool) -> list['EntrySorterTopFinder']:
        return super().sort(entries, reversed)