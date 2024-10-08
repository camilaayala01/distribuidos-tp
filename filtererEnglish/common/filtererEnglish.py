from entryParsing.entryAppIDName import EntryAppIDName
from langid import classify
import logging
from filterer.filterer import Filterer
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.entryAppIDNameReviewText import EntryAppIDNameReviewText
import os

class FiltererEnglish(Filterer):
    def __init__(self):
        super().__init__(EntryAppIDNameReviewText, HeaderWithSender, os.getenv('FILT_ENG'), os.getenv('NODE_ID'))

    def _sendToNext(self, header: HeaderWithSender, filteredEntries: list[EntryAppIDNameReviewText]):
        msg = header.serialize()
        for entry in filteredEntries:
            msg += EntryAppIDName(entry._appID, entry._name).serialize()
        self._internalCommunication.sendToEnglishNegativeReviewsGrouper(msg)

        logging.info(f'action: sending batch to english negative reviews grouper | result: success')

    @classmethod
    def condition(cls, entry: EntryAppIDNameReviewText)-> bool:
        return 'en' == classify(entry.getReviewText())[0]