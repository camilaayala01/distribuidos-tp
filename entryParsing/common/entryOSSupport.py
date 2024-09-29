from entryParsing.common.utils import _boolToInt, _boolToU8, _intToBool


BOOLEAN_BYTES = 1

class EntryOSSupport:
    def __init__(self, windows: bool, mac: bool, linux: bool):
        self._windows =  windows
        self._mac = mac
        self._linux = linux

    def serialize(self) -> bytes:
        windowsBytes = _boolToInt(self._windows).to_bytes(BOOLEAN_BYTES,'big')
        macBytes = _boolToInt(self._mac).to_bytes(BOOLEAN_BYTES,'big')
        linuxBytes = _boolToInt(self._linux).to_bytes(BOOLEAN_BYTES, 'big')
        return windowsBytes + macBytes + linuxBytes

    def __str__(self):
        return f"EntryOSSupport(windows={self._windows}, mac={self._mac}, linux={self._linux})"
    

    @staticmethod
    def deserialize(data: bytes): 
        curr = 0
        entries = []
        while len(data) > curr:
            try:
                windows = int.from_bytes(data[curr:curr+BOOLEAN_BYTES], 'big')
                curr+=BOOLEAN_BYTES
                mac = int.from_bytes(data[curr:curr+BOOLEAN_BYTES], 'big')
                curr+=BOOLEAN_BYTES
                linux = int.from_bytes(data[curr:curr+BOOLEAN_BYTES], 'big')
                curr+=BOOLEAN_BYTES

                entries.append(EntryOSSupport(_intToBool(windows), _intToBool(mac), _intToBool(linux)))

            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    
 

    