from .entry import EntryInterface
from .common.fieldParsing import deserializeBoolean, serializeBoolean

class EntryOSSupport(EntryInterface):
    def __init__(self, _windows: int, _mac: int, _linux: int):
        super().__init__(_windows=_windows, _mac=_mac, _linux=_linux)
    
 

    