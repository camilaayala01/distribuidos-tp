from entryParsing.common.fieldParsing import deserializeCount, serializeCount
from entryParsing.entry import EntryInterface

class EntryOSCount(EntryInterface):
    def __init__(self, _windowsCount: int, _macCount: int, _linuxCount: int, _totalCount: int):
        super().__init__(_windowsCount=_windowsCount, _macCount=_macCount, _linuxCount=_linuxCount, _totalCount=_totalCount)

    def getWindowsCount(self):
        return self._windowsCount
    
    def getMacCount(self):
        return self._macCount
    
    def getLinuxCount(self):
        return self._linuxCount

    def getTotalCount(self):
        return self._totalCount

    def sumEntry(self, entry: 'EntryOSCount'):
        self._windowsCount += entry.getWindowsCount()
        self._macCount += entry.getMacCount()
        self._linuxCount += entry.getLinuxCount()
        self._totalCount += entry.getTotalCount()

    def __str__(self):
        return f"Total de juegos: {str(self._totalCount)}\n\
            Total de juegos soportados en Windows: {str(self._windowsCount)}\n\
                Total de juegos soportados en Linux: {str(self._linuxCount)}\n\
                    Total de juegos soportados en Mac: {str(self._macCount)}"
    