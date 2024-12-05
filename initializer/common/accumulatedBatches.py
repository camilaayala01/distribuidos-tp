import csv
import os
import uuid
from entryParsing.common.fieldParsing import getClientIdUUID
from entryParsing.common.utils import nextRow
from entryParsing.headerInterface import HeaderInterface, HeaderWithTable
from entryParsing.common.table import Table
from packetTracker.defaultTracker import DefaultTracker

MAX_ENTRIES_GAMES = 200
MAX_ENTRIES_REVIEWS = 500

class AccumulatedBatches:
    def __init__(self, clientId: bytes, gamesTracker = None, gamesFragment = 1, reviewsTracker = None, reviewsFragment = 1):
        self._gamesPendingTags = []
        self._reviewsPendingTags = []
        self._accumulatedGames = []
        self._accumulatedPositiveReviews = []
        self._accumulatedNegativeReviews = []
        self._gamesTracker = gamesTracker if gamesTracker else DefaultTracker()
        self._gamesFragment = gamesFragment
        self._reviewsTracker = reviewsTracker if reviewsTracker else DefaultTracker()
        self._reviewsFragment = reviewsFragment 
        self._clientId = clientId
        self._path = f"/{os.getenv('STORAGE')}/{getClientIdUUID(self._clientId)}"

    def isPacketDuplicate(self, header: HeaderWithTable):
        match header.getTable():
            case Table.GAMES:
                return self._gamesTracker.isDuplicate(header)
            case Table.REVIEWS:
                return self._reviewsTracker.isDuplicate(header)
    
    def packetsToAck(self):
        return self._gamesPendingTags + self._reviewsPendingTags
    
    def accumulatedLen(self):
        return len(self._gamesPendingTags) + len(self._reviewsPendingTags)

    def gamesToAck(self):
        return self._gamesPendingTags
    
    def reviewsToAck(self):
        return self._reviewsPendingTags
    
    def consumeGamesToAck(self):
        tags = self._gamesPendingTags
        self._gamesPendingTags = []
        return tags
    
    def consumeReviewsToAck(self):
        tags = self._reviewsPendingTags
        self._reviewsPendingTags = []
        return tags
    
    def consumePacketsToAck(self):
        return self.consumeGamesToAck() + self.consumeReviewsToAck()
    
    def accumulateGames(self, tag, batch, header):
        self._gamesTracker.update(header)
        self._accumulatedGames += batch
        self._gamesPendingTags.append(tag)

    def getGames(self):
        return HeaderWithTable(self._clientId, self._gamesFragment, self._gamesTracker.isDone(), Table.GAMES),\
                self._accumulatedGames

    def accumulateReviews(self, tag, positive, negative, header):
        self._reviewsTracker.update(header)
        self._accumulatedPositiveReviews += positive
        self._accumulatedNegativeReviews += negative
        self._reviewsPendingTags.append(tag)
    
    def getReviews(self):
        return HeaderWithTable(self._clientId, self._reviewsFragment, self._reviewsTracker.isDone(), Table.REVIEWS),\
                self._accumulatedPositiveReviews,\
                self._accumulatedNegativeReviews

    def shouldSendGames(self) -> bool:
        return MAX_ENTRIES_GAMES <= len(self._accumulatedGames) or self._gamesTracker.isDone()

    def shouldSendReviews(self) -> bool:
        return MAX_ENTRIES_REVIEWS <= len(self._accumulatedPositiveReviews)\
            or MAX_ENTRIES_REVIEWS <= len(self._accumulatedNegativeReviews)\
            or self._reviewsTracker.isDone()
    
    def __str__(self):
        return f"tags: {self._gamesPendingTags} | client: {self._clientId} | games tracker: {self._gamesTracker}"

    def resetAccumulatedGames(self):
        self._accumulatedGames = []
        self._gamesFragment += 1

    def storeTracker(self, file, tracker):
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(tracker.asCSVRow())

    def storeFragment(self, file, fragment):
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow([fragment])
        
    def storeMetadata(self):
        with open(self._path + '.tmp', 'w+') as newResults:
            self.storeTracker(file=newResults, tracker=self._gamesTracker)
            self.storeFragment(file=newResults, fragment=self._gamesFragment)
            self.storeTracker(file=newResults, tracker=self._reviewsTracker)
            self.storeFragment(file=newResults, fragment=self._reviewsFragment) 
        os.rename(self._path + '.tmp', self._path + '.csv')

    @staticmethod
    def loadFromStorage(filename)->'AccumulatedBatches':
        path = f"/{os.getenv('STORAGE')}/{filename}"
        clientId = uuid.UUID(filename.removesuffix('.csv')).bytes
        with open(path, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
            gamesTrackerRow = nextRow(reader)
            gamesFragment = nextRow(reader)
            reviewsTrackerRow = nextRow(reader)
            reviewsFragment = nextRow(reader)

        return AccumulatedBatches(
            clientId=clientId, 
            gamesTracker= DefaultTracker.fromStorage(gamesTrackerRow),
            gamesFragment=int(gamesFragment[0]),
            reviewsTracker=DefaultTracker.fromStorage(reviewsTrackerRow),
            reviewsFragment=int(reviewsFragment[0])
            )
            
    def resetAccumulatedReviews(self):
        self._accumulatedPositiveReviews = []
        self._accumulatedNegativeReviews = []
        self._reviewsFragment += 1

    def getClient(self):
        return self._clientId
    
    def getGamesFragment(self): 
        return self._gamesFragment
    
    def getReviewsFragment(self): 
        return self._reviewsFragment