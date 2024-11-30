from entryParsing.entry import EntryInterface
from .common.fieldParsing import deserializeGameName, serializeGameName

class EntryName(EntryInterface):
    def __init__(self, _name: str):
        super().__init__(_name=_name)
    
    @classmethod
    def header(cls):
        return "Name\n"
    