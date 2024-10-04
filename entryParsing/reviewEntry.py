from entryParsing.common.fieldParsing import deserializeAppID, deserializeGameName, deserializeNumber, deserializeReviewText, serializeAppID, serializeGameName, serializeNumber, serializeReviewText
from entryParsing.entry import EntryInterface
from entryParsing.common.utils import getShardingKey

SCORE_LEN = 2
VOTE_LEN = 1

class ReviewEntry(EntryInterface):
    def __init__(self, appID, appName, reviewText, reviewScore, reviewVotes):
        self.appID = appID # max len 6
        self.appName: appName # max len 83
        self.reviewText: reviewText # max len 8873
        self.reviewScore = int(reviewScore) # -1 o 1
        self.reviewVotes = int(reviewVotes) # 0 o 1

    def serialize(self) -> bytes:
        return (serializeAppID(self.appID) + serializeGameName(self.appName) +
               serializeReviewText(self.reviewText) + serializeNumber(self.reviewScore, SCORE_LEN) 
               + serializeNumber(self.reviewVotes, VOTE_LEN))
    
    def isPositive(self) -> bool:
        return True if self.reviewScore == 1 else False

    def serializeForQuery3And5(self) -> bytes:
        return serializeAppID(self.appID)
    
    def serializeForQuery4(self) -> bytes:
        return serializeAppID(self.appID) + serializeReviewText(self.reviewText)

    @classmethod
    def deserialize(cls, data: bytes) -> list['ReviewEntry']: 
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                appID, curr = deserializeAppID(curr, data)
                appName, curr = deserializeGameName(curr, data)
                reviewText, curr = deserializeReviewText(curr, data)
                reviewScore, curr = deserializeNumber(curr,data, SCORE_LEN)
                reviewVotes, curr = deserializeNumber(curr,data, VOTE_LEN)

                entries.append(ReviewEntry(appID, appName,reviewText, reviewScore, reviewVotes))
                
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries
    
    def shardBatch(nodeCount: int, result: list['ReviewEntry']) -> list[bytes]:
        resultingBatches = [bytes() for _ in range(nodeCount)]
        for entry in result:
            shardResult = getShardingKey(entry._id, nodeCount)
            resultingBatches[shardResult] = resultingBatches[shardResult] + entry.serializeForQuery4()