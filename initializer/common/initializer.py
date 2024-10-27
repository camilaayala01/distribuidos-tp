import logging
from entryParsing.common.header import Header
from entryParsing.reducedGameEntry import ReducedGameEntry
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.reviewEntry import ReviewEntry
from entryParsing.entryOSSupport import EntryOSSupport
from entryParsing.entryAppIDNameGenresReleaseDateAvgPlaytime import EntryAppIDNameGenresReleaseDateAvgPlaytime
from entryParsing.entryAppIDNameGenres import EntryAppIDNameGenres
from entryParsing.entryAppID import EntryAppID
from entryParsing.common.utils import getGamesEntryTypeFromEnv, getHeaderTypeFromEnv, getReviewsEntryTypeFromEnv, initializeLog
import os

from sendingStrategy.common.utils import createStrategiesFromNextNodes

MAX_DATA_BYTES = 8000
PRINT_FREQUENCY = 5000

class Initializer:
    def __init__(self): 
        initializeLog()
        queueName = os.getenv('LISTENING_QUEUE')
        self._gamesEntry = getGamesEntryTypeFromEnv()
        self._reviewsEntry = getReviewsEntryTypeFromEnv()
        self._headerType = getHeaderTypeFromEnv()
        self._gamesSendingStrategies = createStrategiesFromNextNodes('GAMES_NEXT_NODES', 'GAMES_NEXT_ENTRIES', 'GAMES_NEXT_HEADERS')
        self._reviewsSendingStrategies = createStrategiesFromNextNodes('REVIEWS_NEXT_NODES', 'REVIEWS_NEXT_ENTRIES')
        self._internalCommunication = InternalCommunication(queueName, os.getenv('NODE_ID'))

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
        header, data = self._headerType.deserialize(body)
        if header.getFragmentNumber() % PRINT_FREQUENCY == 0:
            logging.info(f'action: received msg corresponding to table {header.getTable()} | {header}')

        if header.isGamesTable():
            gameEntries = self._gamesEntry.deserialize(data)
            for index, strategy in enumerate(self._gamesSendingStrategies):
                strategy.send(self._internalCommunication, header, gameEntries)

            ch.basic_ack(delivery_tag = method.delivery_tag)

        elif header.isReviewsTable():
            reviewEntries = self._reviewsEntry.deserialize(data)
            positiveReviewEntries, negativeReviewEntries = self.separatePositiveAndNegative(reviewEntries)
            toSend = [positiveReviewEntries, negativeReviewEntries, negativeReviewEntries]
            for index, strategy in enumerate(self._reviewsSendingStrategies):
                strategy.send(self._internalCommunication, header, toSend[index])
            ch.basic_ack(delivery_tag = method.delivery_tag)

        else:
            raise ValueError()

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)