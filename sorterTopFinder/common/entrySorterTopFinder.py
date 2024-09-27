from abc import ABC, abstractmethod
from typing import Tuple

# Amount of bytes dedicated to stating the length of the name
NAME_LEN = 1 

class EntrySorterTopFinder(ABC):

    def __init__(self, name: str):
        self._name = name

    def serialize(self) -> bytes:
        nameBytes = self._name.encode()
        nameLenByte = len(nameBytes).to_bytes(NAME_LEN, 'big')
        return nameLenByte + nameBytes
    
    @staticmethod
    def deserializeName(curr: int, data: bytes) -> Tuple[int, str]:
        nameLen = int.from_bytes(data[curr:curr + NAME_LEN], 'big')
        curr += NAME_LEN
        name = data[curr:nameLen + curr].decode()
        curr += nameLen

        return curr, name

    @classmethod
    @abstractmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> Tuple['EntrySorterTopFinder', int]:
        pass
    
    @classmethod
    def deserialize(cls, data: bytes) -> list['EntrySorterTopFinder']:
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                entry, curr = cls.deserializeEntry(curr, data)
                entries.append(entry)
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries

    def isGreaterThan(self, otherEntry: 'EntrySorterTopFinder') -> bool:
        return self.getSortingAtribute() > otherEntry.getSortingAtribute()
    
    @abstractmethod
    def getSortingAtribute(self) -> int:
        pass

    @classmethod
    def sort(cls, entries: list['EntrySorterTopFinder']) -> list['EntrySorterTopFinder']:
        return sorted(entries, key=lambda entry: entry.getSortingAtribute(), reverse=True)
