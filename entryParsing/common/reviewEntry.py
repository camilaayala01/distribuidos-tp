from entryParsing.common.fieldParsing import deserializeAppID, deserializeReviewText, serializeAppID, serializeGameName, serializeNumber, serializeReviewText
from entryParsing.entryAppIDReviewText import EntryAppIDReviewText
SCORE_LEN = 2
VOTE_LEN = 1

class ReviewEntry:
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
    
    def deserialize(cls, data: bytes) -> list['ReviewEntry']: 
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                appID, curr = deserializeAppID(curr, data)
                reviewText, curr = deserializeReviewText(curr, data)
                entries.append(EntryAppIDReviewText(appID, reviewText))
                
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries

        