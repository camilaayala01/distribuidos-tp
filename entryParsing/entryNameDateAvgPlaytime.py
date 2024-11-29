# amount of bytes dedicated to stating the length of the name
from entryParsing.common import fieldParsing
from entryParsing.entry import EntryInterface

class EntryNameDateAvgPlaytime(EntryInterface):
    def __init__(self, _name: str, _releaseDate: str, _avgPlaytime: int):
        super().__init__(_name=_name, _releaseDate=_releaseDate, _avgPlaytime=_avgPlaytime)

    def getDate(self) -> str:
        return self._releaseDate