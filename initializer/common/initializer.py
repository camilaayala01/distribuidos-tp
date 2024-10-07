from entryParsing.reducedGameEntry import ReducedGameEntry
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.reviewEntry import ReviewEntry
from entryParsing.entryOSSupport import EntryOSSupport
from entryParsing.entryAppIDNameGenresReleaseDateAvgPlaytime import EntryAppIDNameGenresReleaseDateAvgPlaytime
from entryParsing.entryAppIDNameGenres import EntryAppIDNameGenres
from entryParsing.entryAppID import EntryAppID
import os

class Initializer:
    def __init__(self): 
        self._internalCommunication = InternalCommunication(os.getenv('INIT'), os.getenv('NODE_ID'))

    def separatePositiveAndNegative(self, reviews: list[ReviewEntry]):
        positiveReviewEntries, negativeReviewEntries = [], []
        for entry in reviews:
            if entry.isPositive():
                positiveReviewEntries.append(entry)
            else:
                negativeReviewEntries.append(entry)

        return positiveReviewEntries, negativeReviewEntries

    def handleMessage(self, ch, method, properties, body):
        header, data = HeaderWithTable.deserialize(body)
        serializedHeader = header.serialize()

        if header.isGamesTable():
            gameEntries = ReducedGameEntry.deserialize(data)
            entriesQuery1 = b''.join([EntryOSSupport(entry.windows, entry.mac, entry.linux).serialize() for entry in gameEntries])
            self._internalCommunication.sendToOSCountsGrouper(header.serializeWithoutTable() + entriesQuery1)
            
            entriesQuery2And3 = b''.join([EntryAppIDNameGenresReleaseDateAvgPlaytime(entry.appID, entry.name, entry.genres, entry.releaseDate, entry.avgPlaytime).serialize() for entry in gameEntries])
            self._internalCommunication.sendToIndieFilter(serializedHeader + entriesQuery2And3)

            entriesQuery4And5 = b''.join([EntryAppIDNameGenres(entry.appID, entry.name, entry.genres).serialize() for entry in gameEntries])
            self._internalCommunication.sendToActionFilter(serializedHeader + entriesQuery4And5)
            ch.basic_ack(delivery_tag = method.delivery_tag)
            
        elif header.isReviewsTable():
            reviewEntries = ReviewEntry.deserialize(data)
            positiveReviewEntries, negativeReviewEntries = self.separatePositiveAndNegative(reviewEntries)

            #Query 3
            entriesQuery3 = b''.join([EntryAppID(entry.appID).serialize() for entry in positiveReviewEntries])
            self._internalCommunication.sendToIndiePositiveReviewsGrouper(entriesQuery3)

            #Query 4
            nodeCount = int(os.getenv('JOIN_ENG_NEG_REV_COUNT'))
            shardedResults = ReviewEntry.shardBatch(nodeCount, negativeReviewEntries)

            for i in range(nodeCount):
                self._internalCommunication.sendToActionNegativeReviewsEnglishJoiner(str(i), serializedHeader + shardedResults[i])
 
            # Query 5
            entriesQuery5 = b''.join([EntryAppID(entry.appID).serialize() for entry in negativeReviewEntries])
            self._internalCommunication.sendToActionAllNegativeReviewsGrouper(entriesQuery5)
            ch.basic_ack(delivery_tag = method.delivery_tag)
        
        else:
            raise ValueError()

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)