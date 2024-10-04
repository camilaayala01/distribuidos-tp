from entryParsing.common.fieldParsing import deserializeReviewText, deserializeVariableLenString, serializeReviewText, serializeVariableLenString
from entryParsing.entry import EntryInterface

class EntryAppIDNameReviewText(EntryInterface):
    def __init__(self, appID: str, name: str, reviewText: str):
        self._appID = appID
        self._name = name
        self._reviewText = reviewText

    def serialize(self) -> bytes:
        appIDBytes = serializeVariableLenString(self._appID)
        nameBytes = serializeVariableLenString(self._name)
        reviewTextBytes = serializeReviewText(self._reviewText)
        return appIDBytes + nameBytes + reviewTextBytes

    def __str__(self):
        return f"EntryAppIDNameReviewText(appID={self._appID}, name={self._name}, reviewText={self._reviewText})"
    
    @classmethod
    def deserialize(cls, data: bytes) -> list['EntryAppIDNameReviewText']: 
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                appID, curr = deserializeVariableLenString(curr, data)
                name, curr = deserializeVariableLenString(curr, data)
                reviewText, curr = deserializeReviewText(curr, data)
                entries.append(EntryAppIDNameReviewText(appID, name, reviewText))
                
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    