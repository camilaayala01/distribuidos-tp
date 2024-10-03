from .entryIndieFilterer import EntryIndieFilterer
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.header import Header
import os

class IndieFilterer():
    def __init__(self):
        self._genre = "Indie"
        self._internalCommunication = InternalCommunication("FilterIndie", os.getenv('NODE_ID'))

    def handleMessage(self, ch, method, properties, body):
        header, data = Header.deserialize(body)
        curr = 0
        entries = []
        while len(data) > curr:
            try:
                entry, curr = EntryIndieFilterer.deserializeEntry(curr, data)
                entries.append(entry)
            except:
                raise Exception("Can't deserialize entry")
        filteredEntries = self.filterBatch(entries)
        headerQuery2 = header.serialize()
        headerQuery3 = header.serialize()
        for entry in filteredEntries:
            headerQuery2 += entry.serializeForQuery2()
            headerQuery3 += entry.serializeForQuery3()
        self._internalCommunication.sendToDecadeFilter(headerQuery2)
        self._internalCommunication.sendToReviewsIndieGamesJoiner(headerQuery3)

    def execute(self, data: bytes):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def filterBatch(self, batch: list[EntryIndieFilterer]) -> list[EntryIndieFilterer]:
        return [entry for entry in batch if self._genre in entry.getGenres()]