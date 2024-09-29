# amount of bytes dedicated to stating the length of the name
from typing import Tuple
from datetime import datetime
ID_LEN = 1
NAME_LEN = 1
GENRES_LEN = 1
RELEASE_DATE_LEN = 10
AVG_PLAYTIME_FOREVER_LEN = 4

class EntryIndieFilterer():
    def __init__(self, id: str, name: str, genres: list[str], releaseDate: datetime, avgPlaytimeForever: int):
        self._id = id
        self._name = name
        self._genres = genres
        self._releaseDate = releaseDate
        self._avgPlaytimeForever = avgPlaytimeForever

    def serialize(self) -> bytes:
        serialized = bytes()
        idBytes = self._id.encode()
        serialized += len(idBytes).to_bytes(ID_LEN, 'big') + idBytes
        nameBytes = self._name.encode()
        serialized += len(nameBytes).to_bytes(NAME_LEN, 'big') + nameBytes
        genresBytes = ','.join(self._genres).encode()
        serialized += len(genresBytes).to_bytes(GENRES_LEN, 'big') + genresBytes
        releaseDateBytes = self._releaseDate.strftime("%Y-%m-%d").encode()
        avgPlaytimeForeverBytes = self._avgPlaytimeForever.to_bytes(AVG_PLAYTIME_FOREVER_LEN, 'big')
        return serialized + releaseDateBytes + avgPlaytimeForeverBytes

    #def __str__(self):
    #    return f"EntryIndieFilterer(name={self._name}, avgPlaytime={self._avgPlaytime})"
    
    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> Tuple['EntryIndieFilterer', int]:
        idLen = int.from_bytes(data[curr:curr + ID_LEN], 'big')
        curr += ID_LEN
        id = data[curr:idLen + curr].decode()
        curr += idLen
        nameLen = int.from_bytes(data[curr:curr + NAME_LEN], 'big')
        curr += NAME_LEN
        name = data[curr:nameLen + curr].decode()
        curr += nameLen
        genresLen = int.from_bytes(data[curr:curr + GENRES_LEN], 'big')
        curr += GENRES_LEN
        genres = data[curr:genresLen + curr].decode()
        curr += genresLen
        releaseDate = datetime.strptime(data[curr:RELEASE_DATE_LEN + curr].decode(), "%Y-%m-%d")
        curr += RELEASE_DATE_LEN
        avgPlaytimeForever = int.from_bytes(data[curr:curr + AVG_PLAYTIME_FOREVER_LEN], 'big')
        curr += AVG_PLAYTIME_FOREVER_LEN

        return cls(id, name, genres, releaseDate, avgPlaytimeForever), curr
    
    def getGenres(self) -> list[str]:
        return self._genres