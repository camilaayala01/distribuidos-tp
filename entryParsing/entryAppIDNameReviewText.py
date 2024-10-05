from entryParsing.common.fieldParsing import deserializeAppID, deserializeGameName, deserializeReviewText, serializeAppID, serializeGameName, serializeReviewText
from entryParsing.entry import EntryInterface

class EntryAppIDNameReviewText(EntryInterface):
    def __init__(self, appID: str, name: str, reviewText: str):
        self._appID = appID
        self._name = name
        self._reviewText = reviewText

    def serialize(self) -> bytes:
        appIDBytes = serializeAppID(self._appID)
        nameBytes = serializeGameName(self._name)
        reviewTextBytes = serializeReviewText(self._reviewText)
        return appIDBytes + nameBytes + reviewTextBytes

    def getReviewText(self):
        return self._reviewText

    def __str__(self):
        return f"EntryAppIDNameReviewText(appID={self._appID}, name={self._name}, reviewText={self._reviewText})"
    
    @classmethod
    def deserialize(cls, data: bytes) -> list['EntryAppIDNameReviewText']: 
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                appID, curr = deserializeAppID(curr, data)
                name, curr = deserializeGameName(curr, data)
                reviewText, curr = deserializeReviewText(curr, data)
                entries.append(EntryAppIDNameReviewText(appID, name, reviewText))
                
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    