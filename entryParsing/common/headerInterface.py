import inspect
from entryParsing.common.fieldLen import BOOLEAN_LEN, CLIENT_ID_LEN, COUNT_LEN
from entryParsing.common.fieldParsing import serializeBoolean, serializeCount, getClientID

class HeaderInterface:
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
    
    def serialize(self) -> bytes:
        fragmentBytes = serializeCount(self._fragment)
        eofBytes = serializeBoolean(self._eof)
        return self._clientId + fragmentBytes + eofBytes

    def __str__(self):
        return f"client: {self._clientId} | fragment: {self._fragment} | eof: {self._eof}"
    
    def getClient(self) -> int:
        return self._clientId

    def getFragmentNumber(self) -> int:
        return self._fragment
    
    def isEOF(self) -> bool:
        return self._eof

    @classmethod
    def size(cls):
        return COUNT_LEN + BOOLEAN_LEN + CLIENT_ID_LEN