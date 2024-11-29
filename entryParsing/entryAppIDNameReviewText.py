from entryParsing.common.fieldParsing import deserializeAppID, deserializeGameName, deserializeReviewText, serializeAppID, serializeGameName, serializeReviewText
from entryParsing.entry import EntryInterface

class EntryAppIDNameReviewText(EntryInterface):
    def __init__(self, _appID: str, _name: str, _reviewText: str):
        super().__init__(_appID=_appID, _name=_name, _reviewText=_reviewText)

    def serialize(self) -> bytes:
        appIDBytes = serializeAppID(self._appID)
        nameBytes = serializeGameName(self._name)
        reviewTextBytes = serializeReviewText(self._reviewText)
        return appIDBytes + nameBytes + reviewTextBytes

    def getReviewText(self):
        return self._reviewText

    def __str__(self):
        return f"EntryAppIDNameReviewText(appID={self._appID}, name={self._name}, reviewText={self._reviewText})"