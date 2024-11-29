from entryParsing.entry import EntryInterface
from .common.fieldParsing import deserializeGameName, serializeGameName

class EntryName(EntryInterface):
    def __init__(self, _name: str):
        super().__init__(_name=_name)

    def __str__(self):
        return f"name: {self._name}"
    
    @classmethod
    def header(cls):
        return "Name\n"
    