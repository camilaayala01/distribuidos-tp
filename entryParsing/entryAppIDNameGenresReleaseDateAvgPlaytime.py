from entryParsing.common import fieldParsing
from entryParsing.entry import EntryInterface

class EntryAppIDNameGenresReleaseDateAvgPlaytime(EntryInterface):
    def __init__(self, _appID: str, _name: str, _genres: str, _releaseDate: str, _avgPlaytime: int):
        super().__init__(_appID=_appID, _name=_name, _genres=_genres, _releaseDate=_releaseDate, _avgPlaytime=_avgPlaytime)


    def serialize(self) -> bytes:
        idBytes = fieldParsing.serializeAppID(self._appID)
        nameBytes = fieldParsing.serializeGameName(self._name)
        genresBytes = fieldParsing.serializeGenres(self._genres)
        releaseDateBytes = fieldParsing.serializeReleaseDate(self._releaseDate)
        avgPlaytimeForeverBytes = fieldParsing.serializePlaytime(self._avgPlaytime)
        return idBytes + nameBytes + genresBytes + releaseDateBytes + avgPlaytimeForeverBytes
    
    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> tuple['EntryAppIDNameGenresReleaseDateAvgPlaytime', int]:
        id, curr = fieldParsing.deserializeAppID(curr, data)
        name, curr = fieldParsing.deserializeGameName(curr, data)
        genres, curr = fieldParsing.deserializeGenres(curr, data)
        releaseDate, curr = fieldParsing.deserializeReleaseDate(curr, data)
        avgPlaytimeForever, curr = fieldParsing.deserializePlaytime(curr, data)

        return cls(id, name, genres, releaseDate, avgPlaytimeForever), curr
    
    @classmethod
    def deserialize(cls, data: bytes): 
        curr = 0
        entries = []
        while len(data) > curr:
            try:
                entry, curr = EntryAppIDNameGenresReleaseDateAvgPlaytime.deserializeEntry(curr, data)
                entries.append(entry)
            except:
                raise Exception("Can't deserialize entry")
        return entries

    def getGenres(self) -> str:
        return self._genres