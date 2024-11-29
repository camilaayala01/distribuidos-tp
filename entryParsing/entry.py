from abc import ABC, abstractmethod
import inspect

from .mappers import DESERIALIZERS, SERIALIZERS

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

    def serialize(self) -> bytes:
        signatureConst = inspect.signature(self.__init__)
        params = list(signatureConst.parameters.keys())
        serialized_data = b""
    
        for field in params:
            value = getattr(self, field)
            if field in SERIALIZERS:
                serialized_data += SERIALIZERS[field](value)
            else:
                raise ValueError(f"Serializer not found for field: {field}")
        
        return serialized_data

    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes):
        signatureConst = inspect.signature(cls.__init__)
        params = list(signatureConst.parameters.keys())[1:]

        deserialized_data = {}
        for field in params:
            try:
                if field in DESERIALIZERS:
                    deserialized_data[field], curr = DESERIALIZERS[field](curr, data)
                else:
                    raise ValueError(f"Deserializer not found for field {field}")
            except Exception as e:
                raise ValueError(f"error deserializing field {field}: {e}")
        
        return cls(**deserialized_data), curr

    @classmethod
    def deserialize(cls, data: bytes): 
        curr = 0
        entries = []
        while len(data) > curr:
            try:
                entry, curr = cls.deserializeEntry(curr, data)
                entries.append(entry)
            except Exception as e:
                raise Exception(f"Can't deserialize entry: {e}")
        return entries