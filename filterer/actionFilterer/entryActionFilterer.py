# amount of bytes dedicated to stating the length of the name
from typing import Tuple
ID_LEN = 1
NAME_LEN = 1
GENRES_LEN = 1

class EntryActionFilterer():
    def __init__(self, id: str, name: str, genres: list[str]):
        self._id = id
        self._name = name
        self._genres = genres

    def serialize(self) -> bytes:
        serialized = bytes()
        idBytes = self._id.encode()
        serialized += len(idBytes).to_bytes(ID_LEN, 'big') + idBytes
        nameBytes = self._name.encode()
        serialized += len(nameBytes).to_bytes(NAME_LEN, 'big') + nameBytes
        genresBytes = ','.join(self._genres).encode()
        serialized += len(genresBytes).to_bytes(GENRES_LEN, 'big') + genresBytes
        return serialized

    #def __str__(self):
    #    return f"EntryIndieFilterer(name={self._name}, avgPlaytime={self._avgPlaytime})"
    
    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> Tuple['EntryActionFilterer', int]:
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

        return cls(id, name, genres), curr
    
    def getGenres(self) -> list[str]:
        return self._genres