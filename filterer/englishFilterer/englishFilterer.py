from .entryEnglishFilterer import EntryEnglishFilterer
from langid import classify
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.header import Header
import os

class EnglishFilterer():
    def __init__(self, lang: str):
        self._lang = lang
        self._internalCommunication = InternalCommunication("FilterEnglish", os.getenv('NODE_ID'))

    def handleMessage(self, ch, method, properties, body):
        header, data = Header.deserialize(body)
        curr = 0
        entries = []
        while len(data) > curr:
            try:
                entry, curr = EntryEnglishFilterer.deserializeEntry(curr, data)
                entries.append(entry)
            except:
                raise Exception("Can't deserialize entry")
        filteredEntries = self.filterBatch(entries)
        header = header.serialize()
        # CAMBIAR GETENV Y SEND
        #nodeCount = int(os.getenv('JOIN_ACT_POS_REV_COUNT'))
        #shardedResults = EntryEnglishFilterer.shardBatch(nodeCount, filteredEntries)
        #for i in range(nodeCount):
            #self._internalCommunication.sendToPositiveReviewsActionGamesJoiner(str(i), header + shardedResults[i])

    def execute(self, data: bytes):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def filterBatch(self, batch: list[EntryEnglishFilterer]) -> list[EntryEnglishFilterer]:
        return [entry for entry in batch if self._lang == classify(entry.getReviewText())[0]]