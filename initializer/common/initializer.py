import logging
from entryParsing.reducedGameEntry import ReducedGameEntry
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.reviewEntry import ReviewEntry
from entryParsing.entryOSSupport import EntryOSSupport
from entryParsing.entryAppIDNameGenresReleaseDateAvgPlaytime import EntryAppIDNameGenresReleaseDateAvgPlaytime
from entryParsing.entryAppIDNameGenres import EntryAppIDNameGenres
from entryParsing.entryAppID import EntryAppID
from entryParsing.common.utils import initializeLog
import os

MAX_DATA_BYTES = 8000
PRINT_FREQUENCY = 5000

class Initializer:
    def __init__(self): 
        initializeLog()
        queueName = os.getenv('LISTENING_QUEUE')
        self._internalCommunication = InternalCommunication(queueName, os.getenv('NODE_ID'))
        self._nodeCount = int(os.getenv('JOIN_ACT_COUNT'))

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

    def separatePositiveAndNegative(self, reviews: list[ReviewEntry]):
        positiveReviewEntries, negativeReviewEntries = [], []
        for entry in reviews:
            if entry.isPositive():
                positiveReviewEntries.append(entry)
            else:
                negativeReviewEntries.append(entry)

        return positiveReviewEntries, negativeReviewEntries

    def handleMessage(self, ch, method, _properties, body):
        header, data = HeaderWithTable.deserialize(body)
        if header.getFragmentNumber() % PRINT_FREQUENCY == 0:
            logging.info(f'action: received msg corresponding to table {header.getTable()} | {header}')
        serializedHeader = header.serialize()

        if header.isGamesTable():
            logging.info(f'action: sending Games table batch | result: in progress')
            gameEntries = ReducedGameEntry.deserialize(data)

            entriesQuery1 = b''.join([EntryOSSupport(entry._windows, entry._mac, entry._linux).serialize() for entry in gameEntries])
            self._internalCommunication.sendToOSCountsGrouper(header.serializeWithoutTable() + entriesQuery1)

            entriesQuery2And3 = b''.join([EntryAppIDNameGenresReleaseDateAvgPlaytime(entry._appID, entry._name, entry._genres, entry._releaseDate, entry._avgPlaytime).serialize() for entry in gameEntries])
            self._internalCommunication.sendToIndieFilter(serializedHeader + entriesQuery2And3)

            entriesQuery4And5 = b''.join([EntryAppIDNameGenres(entry._appID, entry._name, entry._genres).serialize() for entry in gameEntries])
            self._internalCommunication.sendToActionFilter(serializedHeader + entriesQuery4And5)

            ch.basic_ack(delivery_tag = method.delivery_tag)
            logging.info(f'action: sending Games table batch | result: success')

        elif header.isReviewsTable():
            logging.info(f'action: sending Reviews table batch | result: in progress | fragment: {header.getFragmentNumber()} | eof: {header.isEOF()}')
            reviewEntries = ReviewEntry.deserialize(data)
            positiveReviewEntries, negativeReviewEntries = self.separatePositiveAndNegative(reviewEntries)

            #Query 3
            entriesQuery3 = b''.join([EntryAppID(entry._appID).serialize() for entry in positiveReviewEntries])
            self._internalCommunication.sendToIndiePositiveReviewsGrouper(serializedHeader + entriesQuery3)

            #Query 4
            shardedResults = ReviewEntry.shardBatch(self._nodeCount, negativeReviewEntries)
            for i in range(self._nodeCount):
                self._internalCommunication.sendToActionNegativeReviewsEnglishJoiner(str(i), serializedHeader + shardedResults[i])

            # Query 5
            entriesQuery5 = b''.join([EntryAppID(entry._appID).serialize() for entry in negativeReviewEntries])
            self._internalCommunication.sendToActionAllNegativeReviewsGrouper(serializedHeader + entriesQuery5)

            ch.basic_ack(delivery_tag = method.delivery_tag)
            logging.info(f'action: sending Reviews table batch | result: success')

        else:
            raise ValueError()

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)