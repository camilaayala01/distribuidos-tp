from .common.fieldParsing import deserializeVariableLenString, serializeVariableLenString

APP_ID_LEN = 1 

class EntryAppID:
    def __init__(self, appID: str):
        self._appID =  appID

    def serialize(self) -> bytes:
        return serializeVariableLenString(self._appID)

    def __str__(self):
        return f"EntryAppID(appID={self._appID})"
    
    @staticmethod
    def deserialize(data: bytes): 
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                appID, curr = deserializeVariableLenString(curr, data)
                entries.append(EntryAppID(appID))
                
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    