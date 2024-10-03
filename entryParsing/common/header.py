from entryParsing.common.fieldParsing import deserializeBoolean, deserializeCount, serializeBoolean, serializeCount
from entryParsing.common.utils import boolToInt, intToBool
FRAGMENT_LEN = 4
EOF_FLAG_LEN = 1

class Header:
    def __init__(self, fragment: int, eof: bool):
        self._fragment = fragment
        self._eof = eof

    def serialize(self) -> bytes:
        fragmentBytes = serializeCount(self._fragment)
        eofBytes = serializeBoolean(self._eof)
        return fragmentBytes + eofBytes

    def __str__(self):
        return f"Header(fragmentNumber={self._fragment}, isEof]{self._eof})"
    
    def getFragmentNumber(self) -> int:
        return self._fragment
    
    def isEOF(self) -> bool:
        return self._eof
    
    @staticmethod
    def deserialize(data: bytes) -> tuple['Header', bytes]: 
        curr = 0
        try:
            fragment, curr = deserializeCount(curr, data)
            eof, curr = deserializeBoolean(curr, data)
            header = Header(fragment, eof)
        except (IndexError, UnicodeDecodeError):
            raise Exception("There was an error parsing data in header")
        
        return header, data[curr:]
   