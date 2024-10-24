from entryParsing.common.fieldLen import BOOLEAN_LEN, COUNT_LEN
from entryParsing.common.fieldParsing import deserializeBoolean, deserializeCount, serializeBoolean, serializeCount, getClientID

class Header:
    def __init__(self, clientId: bytes, fragment: int, eof: bool):
        self._clientId = clientId
        self._fragment = fragment
        self._eof = eof

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
        return COUNT_LEN + BOOLEAN_LEN

    @staticmethod
    def deserialize(data: bytes) -> tuple['Header', bytes]: 
        curr = 0
        try:
            clientId, curr = getClientID(curr, data)
            fragment, curr = deserializeCount(curr, data)
            eof, curr = deserializeBoolean(curr, data)
            header = Header(clientId, fragment, eof)
        except (IndexError, UnicodeDecodeError):
            raise Exception("There was an error parsing data in header")
        
        return header, data[curr:]
   