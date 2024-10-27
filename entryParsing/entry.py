from abc import ABC, abstractmethod
import inspect

class EntryInterface(ABC):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def fromAnother(cls, other, **additionalParams):
        if type(other).__name__ == cls.__name__:
            return other
        params = inspect.signature(cls.__init__).parameters

        validParams = {key: value for key, value in other.__dict__.items() if key in params}
        additionalValidParams = {key: value for key, value in additionalParams.items() if key in params}
        validParams.update(additionalValidParams)
        
        missingParams = [p for p in params if p != 'self' and p not in validParams]
        if missingParams:
            raise ValueError(f"Convertion from class {type(other).__name__} to {cls.__name__} not possible: missing params {missingParams}")
        
        return cls(**validParams)

    @abstractmethod
    def serialize(self) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, data: bytes): 
        pass


