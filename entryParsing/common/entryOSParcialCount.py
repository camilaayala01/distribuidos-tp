from entryParsing.common.utils import _boolToInt, _intToBool
COUNT_BYTES = 4

class EntryOSParcialCount:
    def __init__(self, windows: int, mac: int, linux: int):
        self._windows =  windows
        self._mac = mac
        self._linux = linux

    def serialize(self) -> bytes:
        windowsBytes = _boolToInt(self._windows).to_bytes(COUNT_BYTES,'big')
        macBytes = _boolToInt(self._mac).to_bytes(COUNT_BYTES,'big')
        linuxBytes = _boolToInt(self._linux).to_bytes(COUNT_BYTES, 'big')
        return windowsBytes + macBytes + linuxBytes

    def __str__(self):
        return f"EntryOSParcialCount(windows={self._windows}, mac={self._mac}, linux={self._linux})"
    

    @staticmethod
    def deserialize(data: bytes):      
        curr = 0
        entries = []
        while len(data) > curr:
            try:
                windows = int.from_bytes(data[curr:curr+COUNT_BYTES], 'big')
                curr+=COUNT_BYTES
                mac = int.from_bytes(data[curr:curr+COUNT_BYTES], 'big')
                curr+=COUNT_BYTES
                linux= int.from_bytes(data[curr:curr+COUNT_BYTES], 'big')
                curr+=COUNT_BYTES

                entries.append(EntryOSParcialCount(_intToBool(windows),_intToBool(mac), _intToBool(linux)))

            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    