from uuid import UUID
from entryParsing.common.headerInterface import HeaderInterface
from entryParsing.common.table import Table
from entryParsing.entry import EntryInterface
from packetTracker.defaultTracker import DefaultTracker
import os
import csv

class ActiveClient:
    def __init__(self, clientId: UUID):
        self._clientId = clientId
        self._fragment = 1
        self._games = {} #appid, name
        self._unjoinedReviews = []
        self._joinedEntries = {} #appid, entryType
        self._sent = set() 
        self._gamesTracker = DefaultTracker(clientId)
        self._reviewsTracker = DefaultTracker(clientId)
        self._folderPath = f"/{os.getenv('LISTENING_QUEUE')}/{clientId}/"
        os.makedirs(self._folderPath, exist_ok=True)

    def getId(self):
        return self._clientId.bytes
    
    def destroy(self):
        self._gamesTracker.destroy()
        self._reviewsTracker.destroy()
        if os.path.exists(self.gamesPath() + '.csv'):
            os.remove(self.gamesPath() + '.csv')

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
    
    def storeUnjoinedReviews(self, reviews):
        self._unjoinedReviews.extend(reviews)
    
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

    def copyFile(self, newResultsFile):
        filepath = self.gamesPath() + '.csv'
        if not os.path.exists(filepath):
            return
        fileLen = os.stat(filepath).st_size
        with open(self.gamesPath() + '.csv', 'r+') as currentResults:
            copied = 0
            while copied < fileLen:
                copied += os.copy_file_range(currentResults.fileno(), newResultsFile.fileno(), fileLen)
        
    def storeGamesEntries(self, entries: list[EntryInterface]):
        newResults = open(self.gamesPath() + '.tmp', 'w+')
        self.copyFile(newResults)

        writer = csv.writer(newResults, quoting=csv.QUOTE_MINIMAL)
        for entry in entries:
            written = writer.writerow(entry.__dict__.values())
            if written < entry.expectedCsvLen():
                raise Exception('File could not be written propperly')
        
        newResults.close()
        os.rename(self.gamesPath() + '.tmp', self.gamesPath() + '.csv')