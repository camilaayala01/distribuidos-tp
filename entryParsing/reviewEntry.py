from entryParsing.common import fieldParsing
from entryParsing.entry import EntryInterface

VOTE_LEN = 1

class ReviewEntry(EntryInterface):
    def __init__(self, _appID, _name, _reviewText, _reviewScore, _reviewVotes):
        super().__init__(_appID=_appID, _name=_name, _reviewText=_reviewText,
                         _reviewScore=int(_reviewScore), _reviewVotes=int(_reviewVotes))

    def isPositive(self) -> bool:
        return True if self._reviewScore == 1 else False