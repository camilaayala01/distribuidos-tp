from entryParsing.entry import EntryInterface
from .common.fieldParsing import deserializeGameName, serializeGameName

class EntryName(EntryInterface):
    def __init__(self, name: str):
        self._name =  name

    @staticmethod
    def serialize(self) -> bytes:
        return serializeGameName(self._name)
    
    @staticmethod
    def serializeAll(names: list['EntryName']) -> bytes:
        entryBytes = bytearray()
        for name in names:
            entryBytes.append(name.deserialize())
        return entryBytes

    def __str__(self):
        return f"EntryName(name={self._name})"
    
    @classmethod
    def header(cls):
        return "name\n"
    
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
    