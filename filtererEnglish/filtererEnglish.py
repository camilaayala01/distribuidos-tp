from entryParsing.entryAppIDName import EntryAppIDName
from langid import classify
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
            msg += EntryAppIDName(entry._appID, entry._name)
        self._internalCommunication.sendToPositiveReviewsGrouper(filteredEntries)

    @classmethod
    def condition(cls, entry: EntryAppIDNameReviewText)-> bool:
        return 'en' == classify(entry.getReviewText())[0]