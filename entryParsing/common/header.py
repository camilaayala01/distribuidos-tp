from entryParsing.common.utils import _boolToInt, _intToBool
FRAGMENT_LEN = 4
EOF_FLAG_LEN = 1

class Header:
    def __init__(self, fragment: int, eof: bool):
        self._fragment = fragment
        self._eof = eof

    def serialize(self) -> bytes:
        fragmentBytes = self._fragment.to_bytes(FRAGMENT_LEN, 'big')
        eofBytes = _boolToInt(self._eof).to_bytes(EOF_FLAG_LEN, 'big')
        return fragmentBytes + eofBytes

    def __str__(self):
        return f"Header(fragmentNumber={self._fragment}, isEof]{self._eof})"
    
    @staticmethod
    def deserialize(data: bytes) -> tuple['Header', bytes]: 
        curr = 0
        try:
            fragment = int.from_bytes(data[curr:curr+FRAGMENT_LEN], 'big')
            curr+=FRAGMENT_LEN
            eof = data[curr:EOF_FLAG_LEN+curr].decode()
            curr += EOF_FLAG_LEN
            header = Header(fragment, _intToBool(eof))
        except (IndexError, UnicodeDecodeError):
            raise Exception("There was an error parsing data")
        
        return header, data[curr:len(data)]
   