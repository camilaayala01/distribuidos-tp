from entryParsing.common.fieldParsing import deserializeGameName, deserializePlaytime, serializeGameName, serializePlaytime
from entryParsing.entrySorterTopFinder import EntrySorterTopFinder

class EntryNameAvgPlaytime(EntrySorterTopFinder):
    def __init__(self, _name: str, _avgPlaytime: int):
        super().__init__(_name=_name, _avgPlaytime=_avgPlaytime)  

    def __str__(self):
        return f"{self._name},{self._avgPlaytime};"
    
    def csv(self):
        return f"{self._name},{self._avgPlaytime}\n"

    @classmethod
    def header(self):
        return f"Name,Average playtime forever\n"
    
    def getSortingAtribute(self) -> int:
        return self._avgPlaytime
    
    @classmethod
    def sort(cls, entries: list['EntrySorterTopFinder'], reversed: bool) -> list['EntrySorterTopFinder']:
        return super().sort(entries, reversed)