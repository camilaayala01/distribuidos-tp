# amount of bytes dedicated to stating the length of the name
from typing import Tuple


NAME_LEN = 1 
REVIEW_COUNT_LEN = 4

class EntryNameReviewCount:
    def __init__(self, name: str, reviewCount: int):
        self._name = name
        self._reviewCount = reviewCount

    def serialize(self) -> bytes:
        nameBytes = self._name.encode()
        nameLenByte = len(nameBytes).to_bytes(NAME_LEN, 'big')
        avgPlaytimeBytes = self._reviewCount.to_bytes(REVIEW_COUNT_LEN, 'big')
        return nameLenByte + nameBytes + avgPlaytimeBytes  

    def __str__(self):
        return f"EntryNameReviewCount(name={self._name}, reviewCount={self._avgPlaytime})"
    
    @staticmethod
    def __deserializeEntry(curr, data: bytes) -> Tuple['EntryNameReviewCount', int]:
        nameLen = int.from_bytes(data[curr:curr+NAME_LEN], 'big')
        curr+=NAME_LEN
        name = data[curr:nameLen+curr].decode()
        curr += nameLen
        avgPlaytime = int.from_bytes(data[curr:curr+REVIEW_COUNT_LEN], 'big')
        curr+= REVIEW_COUNT_LEN

        return EntryNameReviewCount(name, avgPlaytime), curr

    @staticmethod
    def deserialize(data: bytes) -> list['EntryNameReviewCount']:
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                entry, curr = EntryNameReviewCount.__deserializeEntry(curr, data)
                entries.append(entry)

            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries

    def isGreaterThan(self, otherEntry: 'EntryNameReviewCount'):
        return self._reviewCount > otherEntry._reviewCount
    
    @staticmethod
    def sort(entries: list['EntryNameReviewCount']) -> list['EntryNameReviewCount']:
        return sorted(entries, key=lambda entry: entry._reviewCount, reverse=True)