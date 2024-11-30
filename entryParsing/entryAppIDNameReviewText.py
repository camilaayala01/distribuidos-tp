from entryParsing.common.fieldParsing import deserializeAppID, deserializeGameName, deserializeReviewText, serializeAppID, serializeGameName, serializeReviewText
from entryParsing.entry import EntryInterface

class EntryAppIDNameReviewText(EntryInterface):
    def __init__(self, _appID: str, _name: str, _reviewText: str):
        super().__init__(_appID=_appID, _name=_name, _reviewText=_reviewText)

    def getReviewText(self):
        return self._reviewText