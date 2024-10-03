from .entryDateFilterer import EntryDateFilterer
from datetime import datetime
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.header import Header
import os

class DateFilterer():
    def __init__(self, bottomDate: datetime, topDate: datetime):
        self._bottomDate = bottomDate
        self._topDate = topDate
        self._internalCommunication = InternalCommunication("FilterDecade", os.getenv('NODE_ID'))

    def handleMessage(self, ch, method, properties, body):
        header, data = Header.deserialize(body)
        curr = 0
        entries = []
        while len(data) > curr:
            try:
                entry, curr = EntryDateFilterer.deserializeEntry(curr, data)
                entries.append(entry)
            except:
                raise Exception("Can't deserialize entry")
        filteredEntries = self.filterBatch(entries)
        header = header.serialize()
        for entry in filteredEntries:
            header += entry.serializeForQuery2()
        self._internalCommunication.sendToAvgPlaytimeSorter(header)

    def execute(self, data: bytes):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def filterBatch(self, batch: list[EntryDateFilterer]) -> list[EntryDateFilterer]:
        return [entry for entry in batch if (self._bottomDate <= entry.getDate() and self._topDate >= entry.getDate())]