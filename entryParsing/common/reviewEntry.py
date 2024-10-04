from client.common.utils import APP_ID_LEN, NAME_LEN, REV_LEN, serializeNumber, serializeString
SCORE_LEN = 2
VOTE_LEN = 1

class Review:
    def __init__(self, appID, appName, reviewText, reviewScore, reviewVotes):
        self.appID = appID # max len 6
        self.appName: appName # max len 83
        self.reviewText: reviewText # max len 8873
        self.reviewScore = int(reviewScore) # -1 o 1
        self.reviewVotes = int(reviewVotes) # 0 o 1

    def serialize(self) -> bytes:
        return (serializeString(self.appID, APP_ID_LEN) + serializeString(self.appName, NAME_LEN) +
               serializeString(self.reviewText, REV_LEN) + serializeNumber(self.reviewScore, SCORE_LEN) 
            + serializeNumber(self.reviewVotes, VOTE_LEN))