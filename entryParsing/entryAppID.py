from entryParsing.entry import EntryInterface
from .common.fieldParsing import deserializeAppID, serializeAppID

class EntryAppID(EntryInterface):
    def __init__(self, _appID: str):
        super().__init__(_appID=_appID)

    def __str__(self):
        return f"AppID:{self._appID})"
    