# amount of bytes dedicated to stating the length of the name
from typing import Tuple
from datetime import datetime
ID_LEN = 1
NAME_LEN = 1
REVIEW_TEXT_LEN = 2

class EntryEnglishFilterer():
    def __init__(self, id: str, name: str, reviewText: str):
        self._id = id
        self._name = name
        self._reviewText = reviewText

    def serialize(self) -> bytes:
        serialized = bytes()
        idBytes = self._id.encode()
        serialized += len(idBytes).to_bytes(ID_LEN, 'big') + idBytes
        nameBytes = self._name.encode()
        serialized += len(nameBytes).to_bytes(NAME_LEN, 'big') + nameBytes
        reviewTextBytes = self._reviewText.encode()
        serialized += len(reviewTextBytes).to_bytes(REVIEW_TEXT_LEN, 'big') + reviewTextBytes
        return serialized

    @classmethod
    def deserializeEntry(cls, curr: int, data: bytes) -> Tuple['EntryEnglishFilterer', int]:
        idLen = int.from_bytes(data[curr:curr + ID_LEN], 'big')
        curr += ID_LEN
        id = data[curr:idLen + curr].decode()
        curr += idLen
        nameLen = int.from_bytes(data[curr:curr + NAME_LEN], 'big')
        curr += NAME_LEN
        name = data[curr:nameLen + curr].decode()
        curr += nameLen
        reviewTextLen = int.from_bytes(data[curr:curr + REVIEW_TEXT_LEN], 'big')
        curr += REVIEW_TEXT_LEN
        reviewText = data[curr:reviewTextLen + curr].decode()
        curr += reviewTextLen

        return cls(id, name, reviewText), curr
    
    def getReviewText(self) -> str:
        return self._reviewText