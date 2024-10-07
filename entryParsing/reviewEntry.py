from entryParsing.common import fieldParsing
from entryParsing.entry import EntryInterface
from entryParsing.common.utils import getShardingKey
from entryParsing.entryAppIDReviewText import EntryAppIDReviewText

SCORE_LEN = 3 
VOTE_LEN = 1

class ReviewEntry(EntryInterface):
    def __init__(self, appID, appName, reviewText, reviewScore, reviewVotes):
            self.appID = appID # max len 6
            self.appName = appName # max len 83
            self.reviewText = reviewText # max len 8873
            self.reviewScore = int(reviewScore)
            self.reviewVotes = int(reviewVotes) # 0 o 1

    def __str__(self):
        return f"EntryReview(appID={self.appID}, name={self.appName})"
    
    def serialize(self) -> bytes:
        return (fieldParsing.serializeAppID(self.appID) + fieldParsing.serializeGameName(self.appName) +
               fieldParsing.serializeReviewText(self.reviewText) + fieldParsing.serializeSignedInt(self.reviewScore)
               + fieldParsing.serializeNumber(self.reviewVotes, VOTE_LEN))

    def isPositive(self) -> bool:
        return True if self.reviewScore == 1 else False 

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

                entries.append(ReviewEntry(appID, appName,reviewText, reviewScore, reviewVotes))
                
            except (IndexError, UnicodeDecodeError, ValueError):
                raise Exception("There was an error parsing data")

        return entries
    
    def shardBatch(nodeCount: int, result: list['ReviewEntry']) -> list[bytes]:
        resultingBatches = [bytes() for _ in range(nodeCount)]
        for entry in result:
            shardResult = getShardingKey(entry.appID, nodeCount)
            resultingBatches[shardResult] = resultingBatches[shardResult] + EntryAppIDReviewText(entry.appID, entry.reviewText).serialize()
        return resultingBatches

