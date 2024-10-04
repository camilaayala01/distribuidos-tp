from entryParsing.entry import EntryInterface
from .common.fieldParsing import deserializeVariableLenString, serializeVariableLenString

class EntryAppIDName(EntryInterface):
    def __init__(self, appID: str, name: str):
        self._appID = appID
        self._name = name

    def serialize(self) -> bytes:
        appIDBytes = serializeVariableLenString(self._appID)
        nameBytes = serializeVariableLenString(self._name)
        return appIDBytes + nameBytes

    def __str__(self):
        return f"EntryAppIDName(appID={self._appID}, name={self._name})"
    
    @classmethod
    def deserialize(cls, data: bytes) -> list['EntryAppIDName']: 
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                appID, curr = deserializeVariableLenString(curr, data)
                name, curr = deserializeVariableLenString(curr, data)
                entries.append(EntryAppIDName(appID, name))
                
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    