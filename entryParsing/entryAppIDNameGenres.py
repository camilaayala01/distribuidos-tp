from entryParsing.common.fieldParsing import deserializeAppID, deserializeGameName, deserializeGenres, serializeAppID, serializeGameName, serializeGenres
from .entry import EntryInterface

class EntryAppIDNameGenres(EntryInterface):
    def __init__(self, _appID: str, _name: str, _genres: str):
        super().__init__(_appID=_appID, _name=_name, _genres=_genres)

    def serialize(self) -> bytes:
        idBytes = serializeAppID(self._appID)
        nameBytes = serializeGameName(self._name)
        genresBytes = serializeGenres(self._genres)
        return idBytes + nameBytes + genresBytes

    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> tuple['EntryAppIDNameGenres', int]:
        id, curr = deserializeAppID(curr, data)
        name, curr = deserializeGameName(curr, data)
        genres, curr = deserializeGenres(curr, data)
        return cls(id, name, genres), curr
    
    @classmethod
    def deserialize(cls, data: bytes): 
        curr = 0
        entries = []
        while len(data) > curr:
            try:
                entry, curr = EntryAppIDNameGenres.deserializeEntry(curr, data)
                entries.append(entry)
            except:
                raise Exception("Can't deserialize entry")
        return entries

    def getGenres(self) -> str:
        return self._genres