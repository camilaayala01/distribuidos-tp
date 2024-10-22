from abc import ABC, abstractmethod
import inspect

class EntryInterface(ABC):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def fromAnother(cls, other):
        if type(other).__name__ == cls.__name__:
            return other
        params = inspect.signature(cls.__init__).parameters
        print(other.__dict__)
        valid_params = {key: value for key, value in other.__dict__.items() if key in params}
        missing_params = [p for p in params if p != 'self' and p not in valid_params]
        if missing_params:
            raise ValueError(f"Convertion from class {type(other).__name__} to {cls.__name__} not possible: missing params {missing_params}")
        return cls(**valid_params)

    @abstractmethod
    def serialize(self) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, data: bytes): 
        pass


