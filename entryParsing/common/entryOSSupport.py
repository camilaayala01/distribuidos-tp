from entryParsing.common.utils import boolToInt, intToBool


BOOLEAN_BYTES = 1

class EntryOSSupport:
    def __init__(self, windows: bool, mac: bool, linux: bool):
        self._windows =  windows
        self._mac = mac
        self._linux = linux

    def serialize(self) -> bytes:
        windowsBytes = boolToInt(self._windows).to_bytes(BOOLEAN_BYTES,'big')
        macBytes = boolToInt(self._mac).to_bytes(BOOLEAN_BYTES,'big')
        linuxBytes = boolToInt(self._linux).to_bytes(BOOLEAN_BYTES, 'big')
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

                entries.append(EntryOSSupport(intToBool(windows), intToBool(mac), intToBool(linux)))

            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    
 

    