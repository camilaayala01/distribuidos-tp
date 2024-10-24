from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface
from packetTracker.defaultTracker import DefaultTracker

class ActiveClient:
    def __init__(self):
        self._fragment = 1
        self._games = {} #appid, name
        self._unjoinedReviews = []
        self._joinedEntries = {} #appid, entryType
        self._sent = set() 
        self._gamesTracker = DefaultTracker()
        self._reviewsTracker = DefaultTracker()

    def finishedReceiving(self):
        return self._gamesTracker.isDone() and self._reviewsTracker.isDone()
    
    def isGameDuplicate(self, header: Header):
        self._gamesTracker.isDuplicate(header)

    def isReviewDuplicate(self, header: Header):
        self._reviewsTracker.isDuplicate(header)

    def updateGamesTracker(self, header: Header):
        self._gamesTracker.update(header)

    def updateReviewsTracker(self, header: Header):
        self._reviewsTracker.update(header)

    def isReviewDuplicate(self, header: Header):
        self._reviewsTracker.isDuplicate(header)

    def isGamesDone(self):
        return self._gamesTracker.isDone()

    def storeGamesEntry(self, entry: EntryInterface):
        self._games[entry._appID] = entry._name