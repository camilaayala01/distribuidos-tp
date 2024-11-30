import shutil
from uuid import UUID
from entryParsing.common.headerInterface import HeaderInterface
from entryParsing.common.table import Table
from entryParsing.entry import EntryInterface
from packetTracker.defaultTracker import DefaultTracker
from entryParsing.common.utils import copyFile, nextRow
import os
import csv

class ActiveClient:
    def __init__(self, clientId: UUID):
        self._clientId = clientId
        self._fragment = 1
        self._joinedEntries = {} #appid, entry[]
        self._gamesTracker = DefaultTracker()
        self._reviewsTracker = DefaultTracker()
        self._folderPath = f"/{os.getenv('LISTENING_QUEUE')}/{clientId}/"
        os.makedirs(self._folderPath, exist_ok=True)

    def getClientIdBytes(self):
        return self._clientId.bytes
    
    def destroy(self):
        if os.path.exists(self._folderPath):
            shutil.rmtree(self._folderPath)

    
    def gamesPath(self):
        return self._folderPath + f'games'

    def reviewsPath(self):
        return self._folderPath + f'reviews'

    def joinedPath(self):
        return self._folderPath + f'joined'

    def finishedReceiving(self):
        return self._gamesTracker.isDone() and self._reviewsTracker.isDone()
    
    def isDuplicate(self, header: HeaderInterface):
        match header.getTable():
            case Table.GAMES:
                return self._gamesTracker.isDuplicate(header)
            case Table.REVIEWS:
               return self._reviewsTracker.isDuplicate(header) 

    def updateTracker(self, header: HeaderInterface):
        match header.getTable():
            case Table.GAMES:
                self._gamesTracker.update(header)
            case Table.REVIEWS:
                self._reviewsTracker.update(header)

    def isGamesDone(self):
        return self._gamesTracker.isDone()
    
    def removeUnjoinedReviews(self):
        if self.unjoinedReviews():
            os.remove(self.reviewsPath() + '.csv')
    
    def unjoinedReviews(self):
        return os.path.exists(self.reviewsPath() + '.csv')

    def loadEntries(self, filepath, entryType):
        if not os.path.exists(filepath):
            return iter([])
        
        with open(filepath, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                yield entryType.fromArgs(row)
    
    def loadGamesEntries(self, entryType):
        return self.loadEntries(self.gamesPath() + '.csv', entryType)

    def loadReviewsEntries(self, entryType):
        return self.loadEntries(self.reviewsPath() + '.csv', entryType)

    def loadJoinedEntries(self, entryType):
        return self.loadEntries(self.joinedPath() + '.csv', entryType)
    
    def storeEntries(self, filepath, entries):
        newResults = open(filepath + '.tmp', 'w+')
        copyFile(newResults, filepath + '.csv')

        writer = csv.writer(newResults, quoting=csv.QUOTE_MINIMAL)
        for entry in entries:
            written = writer.writerow(entry.__dict__.values())
            if written < entry.expectedCsvLen():
                raise Exception('File could not be written propperly')
        
        newResults.close()
        os.rename(filepath + '.tmp', filepath + '.csv')
        
    def storeUnjoinedReviews(self, reviews: list[EntryInterface]):
        self.storeEntries(self.reviewsPath(), reviews)

    def storeGamesEntries(self, entries: list[EntryInterface]):
        self.storeEntries(self.gamesPath(), entries)

    def storeJoinedEntries(self, joinedEntries: dict[EntryInterface], entryType):
        newResults = open(self.joinedPath() + '.tmp', 'w+')
        generator = self.loadJoinedEntries(entryType)
        writer = csv.writer(newResults, quoting=csv.QUOTE_MINIMAL)
        while True:
            entry = nextRow(generator)
            if not entry:
                break
            if entry.getAppID() in joinedEntries:
                entry.addToCount(joinedEntries[entry.getAppID()].getCount())
                joinedEntries.pop(entry.getAppID(), None)
            written = writer.writerow(entry.__dict__.values())
            if written < entry.expectedCsvLen():
                raise Exception('File could not be written propperly')
            
        for entry in joinedEntries.values():
            written = writer.writerow(entry.__dict__.values())
            if written < entry.expectedCsvLen():
                raise Exception('File could not be written propperly')
                        
        newResults.close()
        os.rename(self.joinedPath() + '.tmp', self.joinedPath() + '.csv')
