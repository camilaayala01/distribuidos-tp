from enum import Enum
from entryParsing.common.header import Header
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.entry import EntryInterface

class JoinerConsolidatorType(Enum):
    STREAM = 0
    ENGLISH = 1
    INDIE = 2

    def getResultingHeader(self, header: Header) -> EntryInterface:
        match self:
            case JoinerConsolidatorType.STREAM:
                return HeaderWithQueryNumber(_clientId=header.getClient(), _fragment=header.getFragmentNumber(), _eof=header.isEOF(), _queryNumber=4)
            case JoinerConsolidatorType.INDIE | JoinerConsolidatorType.ENGLISH:
                return header