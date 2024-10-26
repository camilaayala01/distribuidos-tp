from entryParsing.common import fieldParsing
from entryParsing.entry import EntryInterface
from entryParsing.common.utils import getShardingKey
from entryParsing.entryAppIDReviewText import EntryAppIDReviewText

SCORE_LEN = 3 
VOTE_LEN = 1
MAX_REVIEW_TEXT = 150

class ReviewEntry(EntryInterface):
    def __init__(self, _appID, _appName, _reviewText, _reviewScore, _reviewVotes):
        super().__init__(_appID=_appID, _appName=_appName, _reviewText=_reviewText,
                         _reviewScore=int(_reviewScore), _reviewVotes=int(_reviewVotes))

    def __str__(self):
        return f"EntryReview(appID={self.appID}, name={self.appName})"
    
    def serialize(self) -> bytes:
        return (fieldParsing.serializeAppID(self._appID) + fieldParsing.serializeGameName(self._appName) +
               fieldParsing.serializeReviewText(self._reviewText) + fieldParsing.serializeSignedInt(self._reviewScore)
               + fieldParsing.serializeNumber(self._reviewVotes, VOTE_LEN))

    def isPositive(self) -> bool:
        return True if self._reviewScore == 1 else False 

    @classmethod
    def deserialize(cls, data: bytes) -> list['ReviewEntry']: 
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                appID, curr = fieldParsing.deserializeAppID(curr, data)
                appName, curr = fieldParsing.deserializeGameName(curr, data)
                reviewText, curr = fieldParsing.deserializeReviewText(curr, data)
                reviewScore, curr = fieldParsing.deserializeSignedInt(curr, data)
                reviewVotes, curr = fieldParsing.deserializeNumber(curr, data, VOTE_LEN) 

                entries.append(ReviewEntry(appID, appName, reviewText[:MAX_REVIEW_TEXT], reviewScore, reviewVotes))
                
            except (IndexError, UnicodeDecodeError, ValueError):
                raise Exception("There was an error parsing data")

        return entries
    
    def shardBatch(nodeCount: int, result: list['ReviewEntry']) -> list[bytes]:
        resultingBatches = [bytes() for _ in range(nodeCount)]
        for entry in result:
            shardResult = getShardingKey(entry._appID, nodeCount)
            resultingBatches[shardResult] = resultingBatches[shardResult] + EntryAppIDReviewText(entry._appID, entry._reviewText).serialize()
        return resultingBatches

