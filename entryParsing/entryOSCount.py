from entryParsing.common.fieldParsing import deserializeCount, serializeCount
from entryParsing.common.utils import boolToInt, intToBool

class EntryOSCount:
    def __init__(self, windows: int, mac: int, linux: int):
        self._windows =  windows
        self._mac = mac
        self._linux = linux

    def getWindowsCount(self):
        return self._windows
    
    def getMacCount(self):
        return self._mac
    
    def getLinuxCount(self):
        return self._linux

    def serialize(self) -> bytes: 
        windowsBytes = serializeCount(self._windows)
        macBytes = serializeCount(self._mac)
        linuxBytes = serializeCount(self._linux)
        return windowsBytes + macBytes + linuxBytes

    def __str__(self):
        return f"EntryOSCount(windows={self._windows}, mac={self._mac}, linux={self._linux})"

    @staticmethod
    def deserialize(data: bytes):      
        curr = 0
        try:
            windows, curr = deserializeCount(curr, data)
            mac, curr = deserializeCount(curr, data)
            linux, curr = deserializeCount(curr, data)

            return EntryOSCount(windows, mac, linux)

        except (IndexError, UnicodeDecodeError):
            raise Exception("There was an error parsing data")
    