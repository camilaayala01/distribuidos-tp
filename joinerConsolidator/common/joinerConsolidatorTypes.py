from enum import Enum
from entryParsing.common.header import Header
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.entryAppIDNameReviewCount import EntryAppIDNameReviewCount
from entryParsing.entry import EntryInterface
from entryParsing.entryName import EntryName
from entryParsing.entryNameReviewCount import EntryNameReviewCount

class JoinerConsolidatorType(Enum):
    STREAM = 0
    ENGLISH = 1
    INDIE = 2

    def headerType(self) -> type:
        return HeaderWithSender

    def getResultingHeader(self, header: Header) -> EntryInterface:
        match self:
            case JoinerConsolidatorType.STREAM:
                return HeaderWithQueryNumber(fragment=header.getFragmentNumber(), eof=header.isEOF(), queryNumber=4)
            case JoinerConsolidatorType.INDIE | JoinerConsolidatorType.ENGLISH:
                return header