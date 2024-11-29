from entryParsing.common.fieldParsing import deserializeAppID, deserializeGameName, deserializeGenres, serializeAppID, serializeGameName, serializeGenres
from .entry import EntryInterface

class EntryAppIDNameGenres(EntryInterface):
    def __init__(self, _appID: str, _name: str, _genres: str):
        super().__init__(_appID=_appID, _name=_name, _genres=_genres)

    def getGenres(self) -> str:
        return self._genres