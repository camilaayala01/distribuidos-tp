from abc import ABC, abstractmethod

from entryParsing.headerInterface import HeaderInterface

class TrackerInterface(ABC):
    @abstractmethod
    def isDuplicate(self, HeaderInterface: HeaderInterface):
        pass

    @abstractmethod
    def update(self, HeaderInterface: HeaderInterface):
        pass

    @abstractmethod
    def isDone(self):
        pass
    
    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def asCSVRow(self):
        pass
    
    
    
   