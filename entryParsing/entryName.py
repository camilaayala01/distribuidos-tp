from entryParsing.entry import EntryInterface
from .common.fieldParsing import deserializeGameName, serializeGameName

class EntryName(EntryInterface):
    def __init__(self, _name: str):
        super().__init__(_name=_name)

    def serialize(self) -> bytes:
        return serializeGameName(self._name)

    def __str__(self):
        return f"name: {self._name}"
    
    @classmethod
    def header(cls):
        return "Name\n"
    
    def csv(self):
        return f'{self._name}\n'
    
    @classmethod
    def deserialize(cls, data: bytes): 
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                name, curr = deserializeGameName(curr, data)
                entries.append(EntryName(name))
                
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    