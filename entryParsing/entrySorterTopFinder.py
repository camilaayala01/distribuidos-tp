from abc import ABC, abstractmethod
from .entry import EntryInterface

class EntrySorterTopFinder(EntryInterface):

    def __init__(self, name: str):
        self._name = name

    @abstractmethod
    def serialize(self) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> tuple['EntrySorterTopFinder', int]:
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
    def sort(cls, entries: list['EntrySorterTopFinder'], reversed: bool) -> list['EntrySorterTopFinder']:
        return sorted(entries, key=lambda entry: entry.getSortingAtribute(), reverse=reversed)
