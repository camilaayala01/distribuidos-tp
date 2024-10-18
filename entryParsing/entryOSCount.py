from entryParsing.common.fieldParsing import deserializeCount, serializeCount
from entryParsing.common.utils import boolToInt, intToBool
from entryParsing.entry import EntryInterface

class EntryOSCount(EntryInterface):
    def __init__(self, windows: int, mac: int, linux: int, total: int):
        self._windows =  windows
        self._mac = mac
        self._linux = linux
        self._total = total

    def getWindowsCount(self):
        return self._windows
    
    def getMacCount(self):
        return self._mac
    
    def getLinuxCount(self):
        return self._linux

    def getTotalCount(self):
        return self._total

    def sumEntry(self, entry: 'EntryOSCount'):
        self._windows += entry.getWindowsCount()
        self._mac += entry.getMacCount()
        self._linux += entry.getLinuxCount()
        self._total += entry.getTotalCount()

    def serialize(self) -> bytes: 
        windowsBytes = serializeCount(self._windows)
        macBytes = serializeCount(self._mac)
        linuxBytes = serializeCount(self._linux)
        totalBytes = serializeCount(self._total)
        return windowsBytes + macBytes + linuxBytes + totalBytes

    def __str__(self):
        return f"Total de juegos: {str(self._total)}\nTotal de juegos soportados en Windows: {str(self._windows)}\nTotal de juegos soportados en Linux: {str(self._linux)}\nTotal de juegos soportados en Mac: {str(self._mac)}"

    @classmethod
    def deserialize(cls, data: bytes):      
        curr = 0
        try:
            windows, curr = deserializeCount(curr, data)
            mac, curr = deserializeCount(curr, data)
            linux, curr = deserializeCount(curr, data)
            total, _ = deserializeCount(curr, data)
            return EntryOSCount(windows, mac, linux, total)

        except (IndexError, UnicodeDecodeError):
            raise Exception("There was an error parsing data")
    