from .entrySorterTopFinder import EntrySorterTopFinder
from .common.fieldParsing import deserializeSenderID, serializeCount, serializeSenderID

class EntrySenderIDSortedTop:
    def __init__(self, senderID: str, entries: list[EntrySorterTopFinder]):
        self._senderID =  senderID
        self._entries = entries

    def serialize(self):
        senderIDBytes = serializeSenderID(self._senderID)
        entriesBytes = bytes()
        for entry in self._entries:
            entriesBytes + entry.serialize()

        return senderIDBytes + entriesBytes
    
    @classmethod
    def deserialize(cls, entryType: type, data: bytes) -> 'EntrySenderIDSortedTop':
        senderID, curr = deserializeSenderID(0, data)
        entries = entryType.deserialize(data[curr:])

        return EntrySenderIDSortedTop(senderID, entries)
