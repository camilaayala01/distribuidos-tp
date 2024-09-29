BOOLEAN_BYTES = 1

class EntryOSSupport:
    def __init__(self, windows: bool, mac: bool, linux: bool):
        self._windows =  windows
        self._mac = mac
        self._linux = linux

    def serialize(self) -> bytes:
        windowsBytes = self._windows.to_bytes(BOOLEAN_BYTES,'big')
        macBytes = self._mac.to_bytes(BOOLEAN_BYTES,'big')
        linuxBytes = self._mac.to_bytes(BOOLEAN_BYTES, 'big')
        return windowsBytes + macBytes + linuxBytes

    def __str__(self):
        return f"EntryOSSupport(windows={self._windows}, mac={self._mac}, linux={self._linux})"
    

    @staticmethod
    def deserialize(data: bytes): 
        def _u8ToBool(u8: int) -> bool:
            match u8:
                case 1:
                    return False
                case 0:
                    return True
                case _:
                    raise Exception("There was an error parsing data")
                
        curr = 0
        entries = []
        while len(data) > curr:
            try:
                windowsU8 = int.from_bytes(data[curr:curr+BOOLEAN_BYTES], 'big')
                curr+=BOOLEAN_BYTES
                windows = _u8ToBool(windowsU8)
                macU8 = int.from_bytes(data[curr:curr+BOOLEAN_BYTES], 'big')
                curr+=BOOLEAN_BYTES
                mac = _u8ToBool(macU8)
                linuxU8 = int.from_bytes(data[curr:curr+BOOLEAN_BYTES], 'big')
                curr+=BOOLEAN_BYTES
                linux = _u8ToBool(linuxU8)

                entries.append(EntryOSSupport(windows, mac, linux))

            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    
 

    