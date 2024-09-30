from .common.utils import boolToInt, intToBool
from .common.fieldParsing import deserializeBoolean, serializeBoolean

class EntryOSSupport:
    def __init__(self, windows: bool, mac: bool, linux: bool):
        self._windows =  windows
        self._mac = mac
        self._linux = linux

    def serialize(self) -> bytes:
        windowsBytes = serializeBoolean(self._windows)
        macBytes = serializeBoolean(self._mac)
        linuxBytes = serializeBoolean(self._linux)
        return windowsBytes + macBytes + linuxBytes

    def __str__(self):
        return f"EntryOSSupport(windows={self._windows}, mac={self._mac}, linux={self._linux})"
    

    @staticmethod
    def deserialize(data: bytes): 
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
    
 

    