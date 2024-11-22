from enum import Enum
from py3langid.langid import classify
from entryParsing.common.header import Header
from entryParsing.common.headerInterface import HeaderInterface
from entryParsing.entry import EntryInterface

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