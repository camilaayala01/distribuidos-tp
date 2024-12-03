import shutil
from uuid import UUID
from entryParsing.headerInterface import HeaderInterface
from entryParsing.common.table import Table
from entryParsing.messagePart import MessagePartInterface
import os
import csv

from statefulNode.activeClient import ActiveClient

class JoinerClient(ActiveClient):
    def __init__(self, clientId: UUID, gamesTracker, reviewsTracker):
        super().__init__(clientId, fragment=1)
        self._gamesTracker = gamesTracker
        self._reviewsTracker = reviewsTracker
    
    def getFolderPath(self):
        return f"/{os.getenv('LISTENING_QUEUE')}/{self._clientId}/"
    
    def destroy(self):
        if os.path.exists(self.getFolderPath()):
            shutil.rmtree(self.getFolderPath())

    def gamesPath(self):
        return self.getFolderPath() + f'games'

    def reviewsPath(self):
        return self.getFolderPath() + f'reviews'

    def joinedPath(self):
        return self.getFolderPath() + f'joined'

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

    def loadFragment(self):
        self.loadFragmentFromPath(self.joinedPath() + '.csv')
         
    def loadJoinedEntries(self, entryType):
        return self.loadEntries(entryType, self.joinedPath() + '.csv')
    
    def loadAllJoinedEntries(self, entryType):
        return (entry for entry, _ in self.loadEntries(entryType, self.joinedPath() + '.tmp'))

    def loadReviewsEntries(self, entryType):
        return (entry for entry, _ in self.loadEntries(entryType, self.reviewsPath() + '.csv'))

    def loadGamesEntries(self, entryType):
        return (entry for entry, _ in self.loadEntries(entryType, self.gamesPath() + '.csv'))

    def storeTracker(self, file, tracker):
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(tracker.asCSVRow())
    
    def copyEntriesFromCSV(self, srcFilePath, dstFile):
        if not os.path.exists(srcFilePath +'.csv'): 
            return
        writer = csv.writer(dstFile, quoting=csv.QUOTE_MINIMAL)
        with open(srcFilePath +'.csv', 'r') as srcFile:
            reader = csv.reader(srcFile, quoting=csv.QUOTE_MINIMAL)
            next(reader) # skip packet tracker
            for row in reader:
                writer.writerow(row)
        
    def storeEntries(self, entries, filepath, tracker):
        with open(filepath + '.tmp', 'w+') as dstFile:
            self.storeTracker(dstFile, tracker)
            self.copyEntriesFromCSV(srcFilePath=filepath, dstFile=dstFile)
            for entry in entries:
                self.storeEntry(entry, dstFile)

    def storeGamesEntries(self, entries: list[MessagePartInterface]):
        self.storeEntries(entries, self.gamesPath(), self._gamesTracker)
        self.saveNewResults(self.gamesPath())

    def storeUnjoinedReviews(self, reviews: list[MessagePartInterface]):
        self.storeEntries(reviews, self.reviewsPath(), self._reviewsTracker)
        self.saveNewResults(self.reviewsPath())

    def storeFragment(self):
        with open(self.joinedPath() + '.tmp', 'a') as storageFile:
            writer = csv.writer(storageFile, quoting=csv.QUOTE_MINIMAL)
            writer.writerow([self._fragment])

    def storeJoinedEntries(self, entriesToSave: dict[MessagePartInterface], entryType):
        newResults = open(self.joinedPath() + '.tmp', 'w+')
        self.storeTracker(newResults, self._reviewsTracker)
        generator = self.loadJoinedEntries(entryType)
        for data, isFragment in generator:
            if isFragment:
                break
            entry = data
            if entry.getAppID() in entriesToSave:
                entry.addToCount(entriesToSave[entry.getAppID()].getCount())
                entriesToSave.pop(entry.getAppID(), None)
            self.storeEntry(entry, newResults)
            
        for entry in entriesToSave.values():
           self.storeEntry(entry, newResults)
        
        newResults.close()

    def saveNewResults(self, path):
        return os.rename(path + '.tmp', path + '.csv')