from .entryActionFilterer import EntryActionFilterer
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.header import Header
import os

class ActionFilterer():
    def __init__(self):
        self._genre = "Action"
        self._internalCommunication = InternalCommunication("FilterAction", os.getenv('NODE_ID'))

    def handleMessage(self, ch, method, properties, body):
        header, data = Header.deserialize(body)
        curr = 0
        entries = []
        while len(data) > curr:
            try:
                entry, curr = EntryActionFilterer.deserializeEntry(curr, data)
                entries.append(entry)
            except:
                raise Exception("Can't deserialize entry")
        
        filteredEntries = self.filterBatch(entries)
        header = header.serialize()
        nodeCount = int(os.getenv('JOIN_ACT_POS_REV_COUNT'))
        shardedResults = EntryActionFilterer.shardBatch(nodeCount, filteredEntries)
        for i in range(nodeCount):
            self._internalCommunication.sendToPositiveReviewsActionGamesJoiner(str(i), header + shardedResults[i])
        
        nodeCount = int(os.getenv('JOIN_ACT_NEG_REV_COUNT'))
        shardedResults = EntryActionFilterer.shardBatch(nodeCount, filteredEntries)
        for i in range(nodeCount):
            self._internalCommunication.sendToNegativeReviewsActionGamesJoiner(str(i), header + shardedResults[i])


    def execute(self, data: bytes):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def filterBatch(self, batch: list[EntryActionFilterer]) -> list[EntryActionFilterer]:
        return [entry for entry in batch if self._genre in entry.getGenres()]