from entryParsing.common.fieldParsing import deserializeCount, serializeCount
from entryParsing.common.utils import boolToInt, intToBool
from entryParsing.entry import EntryInterface

class EntryOSCount(EntryInterface):
    def __init__(self, _windows: int, _mac: int, _linux: int, _total: int):
        super().__init__(_windows=_windows, _mac=_mac, _linux=_linux, _total=_total)

    def getWindowsCount(self):
        return self._windows
    
    def getMacCount(self):
        return self._mac
    
    def getLinuxCount(self):
        return self._linux

    def getTotalCount(self):
        return self._total
    
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
    