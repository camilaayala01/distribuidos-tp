from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface
from packetTracker.defaultTracker import DefaultTracker
from packetTracker.multiTracker import MultiTracker
from packetTracker.packetTracker import PacketTracker

class ActiveClient:
    def __init__(self, tracker: PacketTracker):
        self._tracker = tracker
        self._partialTop = []

    def __init__(self, initialResults):
        self._fragment = 1
        self._tracker = DefaultTracker()
        self._sent = set()
        self._counts = initialResults

    def __init__(self):
        self._fragment = 1
        self._games = {} #appid, name
        self._unjoinedReviews = []
        self._joinedEntries = {} #appid, entryType
        self._sent = set() 
        self._gamesTracker = DefaultTracker()
        self._reviewsTracker = DefaultTracker()

    def __init__(self, priorNodeCount):
        self._fragment = 1
        self._tracker = MultiTracker(priorNodeCount)

    def isDone(self):
        return self._tracker.isDone()
    
    def update(self, header: Header):
        self._tracker.update(header)
    
    def isDuplicate(self, header: Header) -> bool:
        return self._tracker.isDuplicate(header)

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