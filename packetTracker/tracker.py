from abc import ABC, abstractmethod

from entryParsing.common.header import Header

class TrackerInterface(ABC):
    @abstractmethod
    def isDuplicate(self, header: Header):
        pass

    @abstractmethod
    def update(self, header: Header):
        pass

    @abstractmethod
    def isDone(self):
        pass
    
    @abstractmethod
    def reset(self):
        pass