from entryParsing.common.fieldParsing import deserializeReviewText, deserializeVariableLenString, serializeReviewText, serializeVariableLenString
from entryParsing.entry import EntryInterface

class EntryAppIDReviewText(EntryInterface):
    def __init__(self, appID: str, reviewText: str):
        self._appID = appID
        self._reviewText = reviewText

    def getAppID(self):
        return self._appID

    def getReviewText(self):
        return self._reviewText

    def serialize(self) -> bytes:
        appIDBytes = serializeVariableLenString(self._appID)
        reviewTextBytes = serializeReviewText(self._reviewText)
        return appIDBytes + reviewTextBytes

    def __str__(self):
        return f"EntryAppIDReviewText(appID={self._appID}, reviewText={self._reviewText})"
    
    @classmethod
    def deserialize(cls, data: bytes) -> list['EntryAppIDReviewText']: 
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                appID, curr = deserializeVariableLenString(curr, data)
                reviewText, curr = deserializeReviewText(curr, data)
                entries.append(EntryAppIDReviewText(appID, reviewText))
                
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    