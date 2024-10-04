from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.entryAppIDNameGenres import EntryAppIDNameGenres
from filterer.filtererGenre import Filterer
from internalCommunication.internalCommunication import InternalCommunication
import os

class FiltererAction(Filterer):
    def __init__(self):
        super().__init__(EntryAppIDNameGenres, HeaderWithTable, os.getenv('FILT_ACT'), os.getenv('NODE_ID'))

    def _sendToNext(self, header: HeaderWithTable, filteredEntries: list[EntryAppIDNameGenres]):
        header = header.serialize()
        nodeCount = int(os.getenv('JOIN_ACT_POS_REV_COUNT'))
        shardedResults = EntryAppIDNameGenres.shardBatch(nodeCount, filteredEntries)
        for i in range(nodeCount):
            self._internalCommunication.sendToPositiveReviewsActionGamesJoiner(str(i), header + shardedResults[i])
        
        nodeCount = int(os.getenv('JOIN_ACT_NEG_REV_COUNT'))
        shardedResults = EntryAppIDNameGenres.shardBatch(nodeCount, filteredEntries)
        for i in range(nodeCount):
            self._internalCommunication.sendToNegativeReviewsActionGamesJoiner(str(i), header + shardedResults[i])

    @classmethod
    def condition(cls, entry: EntryAppIDNameGenres) -> bool:
        return "Action" in entry.getGenres()