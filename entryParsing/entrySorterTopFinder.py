from abc import abstractmethod
from .entry import EntryInterface

class EntrySorterTopFinder(EntryInterface):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def isGreaterThanOrEqual(self, otherEntry: 'EntrySorterTopFinder') -> bool:
        return self.getSortingAtribute() >= otherEntry.getSortingAtribute()
    
    @abstractmethod
    def getSortingAtribute(self) -> int:
        pass

    @classmethod
    def sort(cls, entries: list['EntrySorterTopFinder'], reversed: bool) -> list['EntrySorterTopFinder']:
        return sorted(entries, key=lambda entry: entry.getSortingAtribute(), reverse=reversed)
