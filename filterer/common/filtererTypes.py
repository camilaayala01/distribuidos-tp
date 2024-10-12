from enum import Enum
from langid import classify
from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryNameAvgPlaytime import EntryNameAvgPlaytime
from entryParsing.entryNameReleaseDateAvgPlaytime import EntryNameReleaseDateAvgPlaytime

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

    def getResultingEntry(self, entry: EntryInterface, queryNumber: int) -> EntryInterface:
        match self:
            case FiltererType.DECADE:
                return EntryNameAvgPlaytime(entry._name, entry._avgPlaytimeForever)
            case FiltererType.ENGLISH | FiltererType.ACTION:
                return EntryAppIDName(entry._appID, entry._name)
            case FiltererType.INDIE:
                if queryNumber == 2:
                    return EntryNameReleaseDateAvgPlaytime(entry._name, entry._releaseDate, entry._avgPlaytimeForever)
                if queryNumber == 3:
                    return EntryAppIDName(entry._appID, entry._name)

    def getResultingHeader(self, header: Header, queryNumber: int) -> EntryInterface:
        match self:
            case FiltererType.ENGLISH | FiltererType.ACTION | FiltererType.DECADE:
                return header
            case FiltererType.INDIE:
                if queryNumber == 2:
                    return Header(header.getFragmentNumber(), header.isEOF())
                if queryNumber == 3:
                    return header