from entryParsing.entry import EntryInterface
from .common.fieldParsing import deserializeAppID, serializeAppID

class EntryAppID(EntryInterface):
    def __init__(self, appID: str):
        self._appID =  appID

    def serialize(self) -> bytes:
        return serializeAppID(self._appID)

    def __str__(self):
        return f"EntryAppID(appID={self._appID})"
    
    @classmethod
    def deserialize(cls, data: bytes): 
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                appID, curr = deserializeAppID(curr, data)
                entries.append(EntryAppID(appID))
                
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    