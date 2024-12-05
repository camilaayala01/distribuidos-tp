import csv
import os
import uuid
from entryParsing.headerInterface import HeaderInterface
from entryParsing.common.table import Table
from packetTracker.defaultTracker import DefaultTracker

MAX_ENTRIES = 300

class AccumulatedBatches:
    def __init__(self, clientId):
        self._pendingTags = []
        self._accumulatedGames = []
        self._accumulatedPositiveReviews = []
        self._accumulatedNegativeReviews = []
        self._fragment = 1
        self._eof = False
        self._packetTracker = DefaultTracker()
        self._clientId = clientId
        self._path = f"/{os.getenv('LISTENING_QUEUE')}/{self._clientId}/"

    def accumulatedLen(self):
        return len(self._pendingTags)

    def toAck(self):
        self._pendingTags = []
        return self._pendingTags
    
    """
    returns true if could accumulate (same client),
    false if it should already process this entries and begin a new
    accumulator
    """
    def accumulateGames(self, tag, batch, eof, header):
        self._packetTracker.update(header)
        self._accumulatedGames += batch
        self._pendingTags.append(tag)
        self._eof = eof

    def getGames(self):
        return self._accumulatedGames

    def accumulateReviews(self, tag, positive, negative, eof, header):
        self._packetTracker.update(header)
        self._accumulatedPositiveReviews += positive
        self._accumulatedNegativeReviews += negative
        self._pendingTags.append(tag)
        self._eof = eof
    
    def getReviews(self):
        return (self._accumulatedPositiveReviews, self._accumulatedNegativeReviews)

    def shouldSend(self) -> bool:
        return MAX_ENTRIES <= len(self._accumulatedGames) or MAX_ENTRIES <= len(self._accumulatedPositiveReviews) or MAX_ENTRIES <= len(self._accumulatedNegativeReviews) or self._eof

    def __str__(self):
        return f"tags: {self._pendingTags} client: {self._clientId}"

    def resetAccumulatedGames(self):
        self._accumulatedGames = []
        self._fragment += 1
        if self._eof == True:
            self._eof = False
            self._fragment = 1
            self._packetTracker = DefaultTracker()

    def storeTracker(self, file, tracker):
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(tracker.asCSVRow())

    def storeFragment(self):
        with open(self.joinedPath() + '.tmp', 'a') as storageFile:
            writer = csv.writer(storageFile, quoting=csv.QUOTE_MINIMAL)
            writer.writerow([self._fragment])

    def storeMetadata(self, clientID):
        newResults = open(self._path + '.tmp', 'w+')
        self.storeTracker(newResults, self._packetTracker)
        self.storeFragment()   
        newResults.close()
        return os.rename(self._path + '.tmp', self._path + '.csv')

    def resetAccumulatedReviews(self):
        self._accumulatedPositiveReviews = []
        self._accumulatedNegativeReviews = []
        self._fragment += 1

    def getCorrespondingTable(self):
        return self._table

    def getFragment(self):
        return self._fragment

    def getClient(self):
        return self._clientId