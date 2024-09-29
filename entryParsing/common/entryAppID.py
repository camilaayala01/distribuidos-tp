APP_ID_LEN = 1 

class EntryAppID:
    def __init__(self, appID: str):
        self._appID =  appID

    def serialize(self) -> bytes:
        appIDBytes = self._appID.encode()
        appIDLenByte = len(appIDBytes).to_bytes(APP_ID_LEN, 'big')

        return appIDLenByte + appIDBytes

    def __str__(self):
        return f"EntryAppID(appID={self._appID})"
    
    @staticmethod
    def deserialize(data: bytes): 
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                appIDLen = int.from_bytes(data[curr:curr+APP_ID_LEN], 'big')
                curr+=APP_ID_LEN
                appID = data[curr:appIDLen+curr].decode()
                curr += appIDLen

                entries.append(EntryAppID(appID))
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    
 

    