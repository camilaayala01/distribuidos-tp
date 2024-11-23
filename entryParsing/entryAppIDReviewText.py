from entryParsing.common.fieldParsing import deserializeAppID, deserializeReviewText, serializeAppID, serializeReviewText
from entryParsing.entry import EntryInterface

class EntryAppIDReviewText(EntryInterface):
    def __init__(self, _appID: str, _reviewText: str):
        super().__init__(_appID=_appID, _reviewText=_reviewText)

    def getAppID(self):
        return self._appID

    def getReviewText(self):
        return self._reviewText

    def serialize(self) -> bytes:
        appIDBytes = serializeAppID(self._appID)
        reviewTextBytes = serializeReviewText(self._reviewText)
        return appIDBytes + reviewTextBytes

    def __str__(self):
        return f"appID={self._appID}, reviewText={self._reviewText})"
    
    @classmethod
    def deserialize(cls, data: bytes) -> list['EntryAppIDReviewText']: 
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                appID, curr = deserializeAppID(curr, data)
                reviewText, curr = deserializeReviewText(curr, data)
                entries.append(EntryAppIDReviewText(appID, reviewText))
                
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    