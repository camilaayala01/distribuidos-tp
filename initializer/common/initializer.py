import logging
from entryParsing.reducedGameEntry import ReducedGameEntry
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.common.header import Header
from entryParsing.reviewEntry import ReviewEntry
from entryParsing.entryOSSupport import EntryOSSupport
from entryParsing.entryAppIDNameGenresReleaseDateAvgPlaytime import EntryAppIDNameGenresReleaseDateAvgPlaytime
from entryParsing.entryAppIDNameGenres import EntryAppIDNameGenres
from entryParsing.entryAppID import EntryAppID
from entryParsing.common.utils import initializeLog
import os

MAX_DATA_BYTES = 8000

class Initializer:
    def __init__(self): 
        initializeLog()
        queueName = os.getenv('INIT')
        self._internalCommunication = InternalCommunication(queueName, os.getenv('NODE_ID'))
        self._nodeCount = int(os.getenv('JOIN_ENG_NEG_REV_COUNT'))
        self._query_1_games = bytes()
        self._query_2_3_games = bytes()
        self._query_4_5_games = bytes()
        self._query_3_reviews = bytes()
        self._query_4_reviews = [bytes() for _ in range(int(os.getenv('JOIN_ENG_NEG_REV_COUNT')))]
        self._query_5_reviews = bytes()
        self._query_1_games_fragment = 1
        self._query_2_3_games_fragment = 1
        self._query_4_5_games_fragment = 1
        self._query_3_reviews_fragment = 1
        self._query_4_reviews_fragment = [1 for _ in range(int(os.getenv('JOIN_ENG_NEG_REV_COUNT')))]
        self._query_5_reviews_fragment = 1

    def separatePositiveAndNegative(self, reviews: list[ReviewEntry]):
        positiveReviewEntries, negativeReviewEntries = [], []
        for entry in reviews:
            if entry.isPositive():
                positiveReviewEntries.append(entry)
            else:
                negativeReviewEntries.append(entry)

        return positiveReviewEntries, negativeReviewEntries

    def stop(self, _signum, _frame):
        self._internalCommunication.stop()

    def handleMessage(self, ch, method, properties, body):
        header, data = HeaderWithTable.deserialize(body)
        logging.info(f'action: received msg corresponding to table {header.getTable()} | {header}')
        serializedHeader = header.serialize()

        if header.isGamesTable():
            logging.info(f'action: sending Games table batch | result: in progress')
            gameEntries = ReducedGameEntry.deserialize(data)

            #Query 1
            entriesQuery1 = b''.join([EntryOSSupport(entry.windows, entry.mac, entry.linux).serialize() for entry in gameEntries])
            
            if len(entriesQuery1) + len(self._query_1_games) <= MAX_DATA_BYTES:
                self._query_1_games += entriesQuery1
            else:
                headerBytes = Header(self._query_1_games_fragment, False).serialize()
                self._query_1_games_fragment += 1
                self._internalCommunication.sendToOSCountsGrouper(headerBytes + self._query_1_games)
                self._query_1_games = entriesQuery1

            #Query 2 and 3
            entriesQuery2And3 = b''.join([EntryAppIDNameGenresReleaseDateAvgPlaytime(entry.appID, entry.name, entry.genres, entry.releaseDate, entry.avgPlaytime).serialize() for entry in gameEntries])
            
            if len(entriesQuery2And3) + len(self._query_2_3_games) <= MAX_DATA_BYTES:
                self._query_2_3_games += entriesQuery2And3
            else:
                headerBytes = HeaderWithTable(header.getTable(), self._query_2_3_games_fragment, False).serialize()
                self._query_2_3_games_fragment += 1
                self._internalCommunication.sendToIndieFilter(headerBytes + self._query_2_3_games)
                self._query_2_3_games = entriesQuery2And3

            #Query 4 and 5
            entriesQuery4And5 = b''.join([EntryAppIDNameGenres(entry.appID, entry.name, entry.genres).serialize() for entry in gameEntries])
            
            if len(entriesQuery4And5) + len(self._query_4_5_games) <= MAX_DATA_BYTES:
                self._query_4_5_games += entriesQuery4And5
            else:
                headerBytes = HeaderWithTable(header.getTable(), self._query_4_5_games_fragment, False).serialize()
                self._query_4_5_games_fragment += 1
                self._internalCommunication.sendToActionFilter(headerBytes + self._query_4_5_games)
                self._query_4_5_games = entriesQuery4And5

            if header.isEOF():
                headerBytes = Header(self._query_1_games_fragment, True).serialize()
                self._internalCommunication.sendToOSCountsGrouper(headerBytes + self._query_1_games)
                headerBytes = HeaderWithTable(header.getTable(), self._query_2_3_games_fragment, True).serialize()
                self._internalCommunication.sendToIndieFilter(headerBytes + self._query_2_3_games)
                headerBytes = HeaderWithTable(header.getTable(), self._query_4_5_games_fragment, True).serialize()
                self._internalCommunication.sendToActionFilter(headerBytes + self._query_4_5_games)

            ch.basic_ack(delivery_tag = method.delivery_tag)
            logging.info(f'action: sending Games table batch | result: success')

        elif header.isReviewsTable():
            logging.info(f'action: sending Reviews table batch | result: in progress | fragment: {header.getFragmentNumber()} | eof: {header.isEOF()}')
            reviewEntries = ReviewEntry.deserialize(data)
            positiveReviewEntries, negativeReviewEntries = self.separatePositiveAndNegative(reviewEntries)

            #Query 3
            entriesQuery3 = b''.join([EntryAppID(entry.appID).serialize() for entry in positiveReviewEntries])

            if len(entriesQuery3) + len(self._query_3_reviews) <= MAX_DATA_BYTES:
                self._query_3_reviews += entriesQuery3
            else:
                headerBytes = HeaderWithTable(header.getTable(), self._query_3_reviews_fragment, False).serialize()
                self._query_3_reviews_fragment += 1
                self._internalCommunication.sendToIndiePositiveReviewsGrouper(headerBytes + self._query_3_reviews)
                self._query_3_reviews = entriesQuery3

            #Query 4
            shardedResults = ReviewEntry.shardBatch(self._nodeCount, negativeReviewEntries)
            for i in range(self._nodeCount):
                if len(shardedResults[i]) + len(self._query_4_reviews[i]) <= MAX_DATA_BYTES:
                    self._query_4_reviews[i] += shardedResults[i]
                else:
                    headerBytes = HeaderWithTable(header.getTable(), self._query_4_reviews_fragment[i], False).serialize()
                    self._query_4_reviews_fragment[i] += 1
                    self._internalCommunication.sendToActionNegativeReviewsEnglishJoiner(str(i), headerBytes + self._query_4_reviews[i])
                    self._query_4_reviews[i] = shardedResults[i]

            # Query 5
            entriesQuery5 = b''.join([EntryAppID(entry.appID).serialize() for entry in negativeReviewEntries])

            if len(entriesQuery5) + len(self._query_5_reviews) <= MAX_DATA_BYTES:
                self._query_5_reviews += entriesQuery5
            else:
                headerBytes = HeaderWithTable(header.getTable(), self._query_5_reviews_fragment, False).serialize()
                self._query_5_reviews_fragment += 1
                self._internalCommunication.sendToActionAllNegativeReviewsGrouper(headerBytes + self._query_5_reviews)
                self._query_5_reviews = entriesQuery5

            if header.isEOF():
                headerBytes = HeaderWithTable(header.getTable(), self._query_3_reviews_fragment, True).serialize()
                self._internalCommunication.sendToIndiePositiveReviewsGrouper(headerBytes + self._query_3_reviews)

                for i in range(self._nodeCount):
                    headerBytes = HeaderWithTable(header.getTable(), self._query_4_reviews_fragment[i], True).serialize()
                    self._internalCommunication.sendToActionNegativeReviewsEnglishJoiner(str(i), headerBytes + self._query_4_reviews[i])

                headerBytes = HeaderWithTable(header.getTable(), self._query_5_reviews_fragment, True).serialize()
                self._internalCommunication.sendToActionAllNegativeReviewsGrouper(headerBytes + self._query_5_reviews)

            ch.basic_ack(delivery_tag = method.delivery_tag)
            logging.info(f'action: sending Reviews table batch | result: success')

        else:
            raise ValueError()

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)