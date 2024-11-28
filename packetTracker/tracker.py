from abc import ABC, abstractmethod
import re

from entryParsing.common.header import Header
from packetTracker.defaultTracker import DefaultTracker

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

    @abstractmethod
    def asCSVRow(self):
        pass
    
    
    
   