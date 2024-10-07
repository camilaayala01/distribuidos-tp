# amount of bytes dedicated to stating the length of the name
from typing import Tuple
from entryParsing.common import fieldParsing
from entryParsing.entry import EntryInterface

class EntryAppIDNameGenresReleaseDateAvgPlaytime(EntryInterface):
    def __init__(self, id: str, name: str, genres: str, releaseDate: str, avgPlaytimeForever: int):
        self._id = id
        self._name = name
        self._genres = genres
        self._releaseDate = releaseDate
        self._avgPlaytimeForever = avgPlaytimeForever

    def serialize(self) -> bytes:
        idBytes = fieldParsing.serializeAppID(self._id)
        nameBytes = fieldParsing.serializeGameName(self._name)
        genresBytes = fieldParsing.serializeGenres(self._genres)
        releaseDateBytes = fieldParsing.serializeReleaseDate(self._releaseDate)
        avgPlaytimeForeverBytes = fieldParsing.serializePlaytime(self._avgPlaytimeForever)
        return idBytes + nameBytes + genresBytes + releaseDateBytes + avgPlaytimeForeverBytes
    
    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> Tuple['EntryAppIDNameGenresReleaseDateAvgPlaytime', int]:
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