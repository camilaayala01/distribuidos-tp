from .common.fieldParsing import deserializeCount, deserializeVariableLenString, serializeCount, serializeVariableLenString
from .entry import EntryInterface

class EntryAppIDNameReviewCount(EntryInterface):
    def __init__(self, appID: str, name: str, count: int):
        self._appID =  appID
        self._name = name
        self._count = count

    def getAppID(self):
        return self._appID
    
    def getName(self):
        return self._name
    
    def getCount(self):
        return self._count
    
    def serialize(self) -> bytes:
        appIDBytes = serializeVariableLenString(self._appID)
        nameBytes = serializeVariableLenString(self._appID)
        countBytes = serializeCount(self._count)

        return appIDBytes + nameBytes + countBytes

    def __str__(self):
        return f"EntryAppIDNameReviewCount(appID={self._appID}, name={self._name}, count={self._count})"

    @classmethod
    def deserialize(cls, data: bytes): 
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                appID, curr = deserializeVariableLenString(curr, data)
                name, curr = deserializeVariableLenString(curr, data)
                reviewCount, curr = deserializeCount(curr, data)
                entries.append(EntryAppIDNameReviewCount(appID, name, reviewCount))
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries