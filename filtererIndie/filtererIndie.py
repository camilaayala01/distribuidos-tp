from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryAppIDNameGenresReleaseDateAvgPlaytime import EntryAppIDNameGenresReleaseDateAvgPlaytime
from entryParsing.entryNameReleaseDateAvgPlaytime import EntryNameReleaseDateAvgPlaytime
from filterer.filterer import Filterer
from entryParsing.common.header import Header
import os

class FiltererIndie(Filterer):
    def __init__(self):
        super().__init__(EntryAppIDNameGenresReleaseDateAvgPlaytime, HeaderWithTable, os.getenv('FILT_INDIE'), os.getenv('NODE_ID'))

    def _sendToNext(self, header: HeaderWithTable, filteredEntries: list[EntryAppIDNameGenresReleaseDateAvgPlaytime]):
        forQuery2 = Header(header.getFragmentNumber(), header.isEOF()).serialize()
        forQuery3 = header.serialize()
        
        listQuery3 = []
        for entry in filteredEntries:
            forQuery2 += EntryNameReleaseDateAvgPlaytime(entry._name, entry._releaseDate, entry._avgPlaytimeForever).serialize()
            listQuery3 += [EntryAppIDName(entry._id, entry._name)]

        listQuery3 = EntryAppIDName.shardBatch(listQuery3, os.getenv('JOIN_INDIE_REV_COUNT'))

        self._internalCommunication.sendToDecadeFilter(forQuery2)

        for i in range(os.getenv('JOIN_INDIE_REV_COUNT')):
            self._internalCommunication.sendToReviewsIndieGamesJoiner(str(i), forQuery3 + listQuery3[i])

    @classmethod
    def condition(cls, entry: EntryAppIDNameGenresReleaseDateAvgPlaytime)-> bool:
        return "Indie" in entry.getGenres()