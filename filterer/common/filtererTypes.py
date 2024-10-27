from enum import Enum
import os
from py3langid.langid import classify
from entryParsing.common.header import Header
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.entry import EntryInterface
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryAppIDNameGenres import EntryAppIDNameGenres
from entryParsing.entryAppIDNameGenresReleaseDateAvgPlaytime import EntryAppIDNameGenresReleaseDateAvgPlaytime
from entryParsing.entryAppIDNameReviewText import EntryAppIDNameReviewText
from entryParsing.entryNameAvgPlaytime import EntryNameAvgPlaytime
from entryParsing.entryNameDateAvgPlaytime import EntryNameDateAvgPlaytime

class FiltererType(Enum):
    DECADE = 0
    INDIE = 1
    ACTION = 2
    ENGLISH = 3

    def executeCondition(self, entry: EntryInterface) -> bool:
        match self:
            case FiltererType.DECADE:
                return "201" in entry.getDate()
            case FiltererType.ENGLISH:
                return 'en' == classify(entry.getReviewText())[0]
            case FiltererType.INDIE:
                return "indie" in entry.getGenres().lower()
            case FiltererType.ACTION:
                return "action" in entry.getGenres().lower()

    def getResultingHeader(self, header: Header, nextNodeName: str) -> EntryInterface:
        match self:
            case FiltererType.ENGLISH | FiltererType.ACTION | FiltererType.DECADE:
                return header
            case FiltererType.INDIE:
                if nextNodeName == "FilterDecade":
                    return Header(header.getClient(), header.getFragmentNumber(), header.isEOF())
                if nextNodeName == "JoinerIndiePositiveReviews":
                    return header