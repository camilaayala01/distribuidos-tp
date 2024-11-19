from abc import ABC, abstractmethod
import inspect

class EntryInterface(ABC):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def expectedCsvLen(self):
        fieldsLen = sum(len(str(value)) for value in self.__dict__.values())
        return max(0, len(self.__dict__.values()) - 1) + fieldsLen + len('\n')
    
    @classmethod
    def fromArgs(cls, args: list[str]):
        params = list(inspect.signature(cls.__init__).parameters.items())[1:]
        dataTypes = [param.annotation for _, param in params]
        convertedArgs = [cast(arg) if arg else None for cast, arg in zip(dataTypes, args)]
        kwargs = {param[0]: value for param, value in zip(params, convertedArgs)}
        return cls(**kwargs)
    
    def csv(self):
        return ','.join(map(str, self.__dict__.values())) + '\n'
        
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


