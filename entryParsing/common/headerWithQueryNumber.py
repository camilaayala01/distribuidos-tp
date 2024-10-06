from .header import Header
from .fieldParsing import deserializeBoolean, deserializeCount, deserializeQueryNumber, serializeQueryNumber
from entryParsing.common.fieldLen import QUERY_NUMBER_LEN

class HeaderWithQueryNumber(Header):
    def __init__(self, fragment: int, eof: bool, queryNumber: int):
        super().__init__(fragment, eof)
        self._queryNumber = queryNumber

    def serialize(self) -> bytes:
        return  super().serialize() + serializeQueryNumber(self._queryNumber)
    
    @classmethod
    def size(cls):
        return super().size() + QUERY_NUMBER_LEN

    @staticmethod
    def deserialize(data: bytes) -> tuple['Header', bytes]:
        curr = 0
        try:
            fragment, curr = deserializeCount(curr, data)
            eof, curr = deserializeBoolean(curr, data)
            queryNum, curr = deserializeQueryNumber(curr, data)
        except (IndexError, UnicodeDecodeError):
            raise Exception("There was an error parsing data in header")
        
        return HeaderWithQueryNumber(fragment, eof, queryNum), data[curr:]