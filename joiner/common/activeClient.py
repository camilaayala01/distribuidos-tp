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
    def __init__(self, clientId: UUID, gamesTracker, reviewsTracker):
        self._clientId = clientId
        self._fragment = 1
        self._gamesTracker = gamesTracker
        self._reviewsTracker = reviewsTracker
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

    def loadFragment(self):
        filepath = self.joinedPath() + '.csv'
        if not os.path.exists(filepath):
            return
        with open(filepath, 'rb') as file:
            file.seek(-2, os.SEEK_END)
            while file.read(1) != b'\n':
                file.seek(-2, os.SEEK_CUR)
            lastLine = file.readline().decode().strip()
        self._fragment = int(lastLine)

    def loadEntries(self, entryType, filepath):
        if not os.path.exists(filepath):
            return iter([])
        
        with open(filepath, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
            next(reader) # skip packet tracker
            for row in reader:
                try:
                    yield entryType.fromArgs(row), False
                except TypeError:
                    # reached end of entries, got to fragment number
                    yield int(row[0]), True
         
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
            writer = csv.writer(dstFile, quoting=csv.QUOTE_MINIMAL)
            for entry in entries:
                written = writer.writerow(entry.__dict__.values())
                if written < entry.expectedCsvLen():
                    raise Exception('File could not be written properly')

    def storeGamesEntries(self, entries: list[EntryInterface]):
        self.storeEntries(entries, self.gamesPath(), self._gamesTracker)
        self.saveNewResults(self.gamesPath())

    def storeUnjoinedReviews(self, reviews: list[EntryInterface]):
        self.storeEntries(reviews, self.reviewsPath(), self._reviewsTracker)
        self.saveNewResults(self.reviewsPath())

    def storeFragment(self):
        with open(self.joinedPath() + '.tmp', 'a') as storageFile:
            writer = csv.writer(storageFile, quoting=csv.QUOTE_MINIMAL)
            writer.writerow([self._fragment])

    def storeJoinedEntries(self, entriesToSave: dict[EntryInterface], entryType):
        newResults = open(self.joinedPath() + '.tmp', 'w+')
        writer = csv.writer(newResults, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(self._reviewsTracker.asCSVRow())
        generator = self.loadJoinedEntries(entryType)
        for data, isFragment in generator:
            if isFragment:
                break
            entry = data
            if entry.getAppID() in entriesToSave:
                entry.addToCount(entriesToSave[entry.getAppID()].getCount())
                entriesToSave.pop(entry.getAppID(), None)
            written = writer.writerow(entry.__dict__.values())
            if written < entry.expectedCsvLen():
                raise Exception('File could not be written propperly')
            
        for entry in entriesToSave.values():
            written = writer.writerow(entry.__dict__.values())
            if written < entry.expectedCsvLen():
                raise Exception('File could not be written propperly')
        
        newResults.close()

    def saveNewResults(self, path):
        os.rename(path + '.tmp', path + '.csv')