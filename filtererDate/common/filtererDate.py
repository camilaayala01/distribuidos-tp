from entryParsing.entryNameDateAvgPlaytime import EntryNameDateAvgPlaytime
from entryParsing.entryNameAvgPlaytime import EntryNameAvgPlaytime
from filterer.filterer import Filterer
from entryParsing.common.header import Header
from entryParsing.common.utils import getShardingKey
import os
import logging

class FiltererDate(Filterer):
    def __init__(self):
        super().__init__(EntryNameDateAvgPlaytime, Header, os.getenv('FILT_DEC'), os.getenv('NODE_ID'))

    def _sendToNext(self, header: Header, filteredEntries: list[EntryNameDateAvgPlaytime]):
        serializedHeader = header.serialize()

        for entry in filteredEntries:
            serializedHeader += EntryNameAvgPlaytime(entry._name, entry._avgPlaytimeForever).serialize()

        shardingKey = getShardingKey(header.getFragmentNumber(), int(os.getenv('SORT_AVG_PT_COUNT')))
        if header.isEOF():
            for i in range(int(os.getenv('SORT_AVG_PT_COUNT'))):
                if shardingKey == i:
                    self._internalCommunication.sendToAvgPlaytimeSorter(str(i), serializedHeader)
                    continue
                self._internalCommunication.sendToAvgPlaytimeSorter(str(i), header.serialize())
        else:
            self._internalCommunication.sendToAvgPlaytimeSorter(str(shardingKey), serializedHeader)

        logging.info(f'action: sending batch to average playtime sorter | result: success')
    
    @classmethod
    def condition(cls, entry: EntryNameDateAvgPlaytime):
        return "201" in entry.getDate()