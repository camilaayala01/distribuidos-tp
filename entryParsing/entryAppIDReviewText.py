from entryParsing.common.fieldParsing import deserializeAppID, deserializeReviewText, serializeAppID, serializeReviewText
from entryParsing.entry import EntryInterface

class EntryAppIDReviewText(EntryInterface):
    def __init__(self, _appID: str, _reviewText: str):
        super().__init__(_appID=_appID, _reviewText=_reviewText)

    def getAppID(self):
        return self._appID

    def getReviewText(self):
        return self._reviewText