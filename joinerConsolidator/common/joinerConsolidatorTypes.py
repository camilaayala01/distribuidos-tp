from enum import Enum
from entryParsing.common.header import Header
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.entry import EntryInterface
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryAppIDNameGenres import EntryAppIDNameGenres
from entryParsing.entryAppIDNameGenresReleaseDateAvgPlaytime import EntryAppIDNameGenresReleaseDateAvgPlaytime
from entryParsing.entryAppIDNameReviewCount import EntryAppIDNameReviewCount
from entryParsing.entryAppIDNameReviewText import EntryAppIDNameReviewText
from entryParsing.entryName import EntryName
from entryParsing.entryNameAvgPlaytime import EntryNameAvgPlaytime
from entryParsing.entryNameDateAvgPlaytime import EntryNameDateAvgPlaytime
from entryParsing.entryNameReleaseDateAvgPlaytime import EntryNameReleaseDateAvgPlaytime
from entryParsing.entryNameReviewCount import EntryNameReviewCount

class JoinerConsolidatorType(Enum):
    STREAM = 0
    ENGLISH = 1
    INDIE = 2

    def entryType(self) -> type:
        match self:
            case JoinerConsolidatorType.STREAM:
                return EntryName
            case JoinerConsolidatorType.ENGLISH:
                return EntryAppIDNameReviewCount
            case JoinerConsolidatorType.INDIE:
                return EntryNameReviewCount

    def headerType(self) -> type:
        return HeaderWithSender

    def getResultingHeader(self, header: Header) -> EntryInterface:
        match self:
            case JoinerConsolidatorType.STREAM:
                return HeaderWithQueryNumber(fragment=header.getFragmentNumber(), eof=header.isEOF(), queryNumber=4)
            case JoinerConsolidatorType.INDIE | JoinerConsolidatorType.ENGLISH:
                return header