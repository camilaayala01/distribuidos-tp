from abc import ABC, abstractmethod

class EntryInterface(ABC):
    @abstractmethod
    def serialize(self) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, data: bytes): 
        pass


