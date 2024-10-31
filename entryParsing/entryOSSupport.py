from .entry import EntryInterface
from .common.fieldParsing import deserializeBoolean, serializeBoolean

class EntryOSSupport(EntryInterface):
    def __init__(self, _windows: int, _mac: int, _linux: int):
        super().__init__(_windows=_windows, _mac=_mac, _linux=_linux)

    def serialize(self) -> bytes:
        windowsBytes = serializeBoolean(self._windows)
        macBytes = serializeBoolean(self._mac)
        linuxBytes = serializeBoolean(self._linux)
        return windowsBytes + macBytes + linuxBytes

    def __str__(self):
        return f"EntryOSSupport(windows={self._windows}, mac={self._mac}, linux={self._linux})"
    
    @classmethod
    def deserialize(cls, data: bytes): 
        curr = 0
        entries = []
        while len(data) > curr:
            try:
                windows, curr = deserializeBoolean(curr, data)
                mac, curr = deserializeBoolean(curr, data)
                linux, curr = deserializeBoolean(curr, data)

                entries.append(EntryOSSupport(windows, mac, linux))

            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    
 

    