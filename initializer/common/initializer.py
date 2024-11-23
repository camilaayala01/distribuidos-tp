import logging
from internalCommunication.common.utils import createStrategiesFromNextNodes
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.reviewEntry import ReviewEntry
from entryParsing.common.utils import getGamesEntryTypeFromEnv, getHeaderTypeFromEnv, getReviewsEntryTypeFromEnv, initializeLog
import os

from internalCommunication.internalMessageType import InternalMessageType

PRINT_FREQUENCY = 300

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

    def handleDataMessage(self, body):
        header, data = self._headerType.deserialize(body)
        if header.getFragmentNumber() % PRINT_FREQUENCY == 0:
            logging.info(f'action: received msg corresponding to table {header.getTable()} | {header}')

        if header.isGamesTable():
            gameEntries = self._gamesEntry.deserialize(data)
            for index, strategy in enumerate(self._gamesSendingStrategies):
                strategy.sendData(self._internalCommunication, header, gameEntries)
        elif header.isReviewsTable():
            reviewEntries = self._reviewsEntry.deserialize(data)
            positiveReviewEntries, negativeReviewEntries = self.separatePositiveAndNegative(reviewEntries)
            toSend = [positiveReviewEntries, negativeReviewEntries, negativeReviewEntries]
            for index, strategy in enumerate(self._reviewsSendingStrategies):
                strategy.sendData(self._internalCommunication, header, toSend[index])
        else:
            raise ValueError("Table is not one of the two allowed tables")
        
    def handleMessage(self, ch, method, _properties, body):
        msgType, msg = InternalMessageType.deserialize(body)
        match msgType:
            case InternalMessageType.DATA_TRANSFER:
                self.handleDataMessage(msg)
            case InternalMessageType.CLIENT_FLUSH:
                # only to games receivers, as they all end up in the same place -> a joiner
                for strategy in self._gamesSendingStrategies:
                    strategy.sendFlush(middleware=self._internalCommunication, clientId=msg)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)