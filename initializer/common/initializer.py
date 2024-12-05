import csv
import logging
import uuid
from entryParsing.headerInterface import HeaderInterface
from entryParsing.reducedGameEntry import ReducedGameEntry
from healthcheckAnswerController.healthcheckAnswerController import HealthcheckAnswerController
from packetTracker.defaultTracker import DefaultTracker
from .accumulatedBatches import AccumulatedBatches
from internalCommunication.common.utils import createStrategiesFromNextNodes
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.fullEntry import ReviewEntry
from entryParsing.common.utils import getHeaderTypeFromEnv, initializeLog, nextRow
import os

from internalCommunication.internalMessageType import InternalMessageType

PREFETCH_COUNT = int(os.getenv('PREFETCH_COUNT'))

class Initializer:
    def __init__(self): 
        initializeLog()
        queueName = os.getenv('LISTENING_QUEUE')
        self._gamesEntry = ReducedGameEntry
        self._reviewsEntry = ReviewEntry
        self._headerType = getHeaderTypeFromEnv()
        self._gamesSendingStrategies = createStrategiesFromNextNodes('GAMES_NEXT_NODES', 'GAMES_NEXT_ENTRIES', 'GAMES_NEXT_HEADERS')
        self._reviewsSendingStrategies = createStrategiesFromNextNodes('REVIEWS_NEXT_NODES', 'REVIEWS_NEXT_ENTRIES')
        self._internalCommunication = InternalCommunication(queueName, os.getenv('NODE_ID'))
        self._healthcheckAnswerController = HealthcheckAnswerController()
        self._healthcheckAnswerController.execute()
        self._accumulatedBatchesByID = {}     
        self.loadStatesFromDisk()
        os.makedirs(f"/{os.getenv('STORAGE')}/", exist_ok=True)

    def loadStatesFromDisk(self):
        dataDirectory = f"/{os.getenv('STORAGE')}/"
        if not os.path.exists(dataDirectory) or not os.path.isdir(dataDirectory):
            return
        for filename in os.listdir(dataDirectory):
            path = os.path.join(dataDirectory, filename)
            if not os.path.isfile(path): 
                continue

            if path.endswith('.csv'):
                accumulatedBatches = AccumulatedBatches.loadFromStorage(filename)
                self._accumulatedBatchesByID[accumulatedBatches.getClient()] = accumulatedBatches
            else:
                os.remove(path)

    def stop(self, _signum, _frame):
        self._internalCommunication.stop()
        self._healthcheckAnswerController.stop()

    def separatePositiveAndNegative(self, reviews: list[ReviewEntry]):
        positiveReviewEntries, negativeReviewEntries = [], []
        for entry in reviews:
            if entry.isPositive():
                positiveReviewEntries.append(entry)
            else:
                negativeReviewEntries.append(entry)
        return positiveReviewEntries, negativeReviewEntries

    def createTrackerFromRow(self, row):
        return DefaultTracker.fromStorage(row)
    
    def loadTrackerFromFile(self, filepath):
        with open(filepath, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
            packetTrackerRow = nextRow(reader)
        return self.createTrackerFromRow(packetTrackerRow)

    def reachedCapacity(self):
        return sum(batches.accumulatedLen() for batches in self._accumulatedBatchesByID.values()) >= PREFETCH_COUNT

    def handleGames(self, accumulatedBatches: AccumulatedBatches, tag: int, header: HeaderInterface, data: bytes):
        gameEntries = self._gamesEntry.deserialize(data)
        accumulatedBatches.accumulateGames(tag, gameEntries, header)
        if accumulatedBatches.shouldSendGames():
            self.sendGames(accumulatedBatches)
            return True
        return False

    def sendGames(self, accumulatedBatches):
        if not accumulatedBatches.gamesToAck():
            return
        header, gameEntries = accumulatedBatches.getGames()
        for _, strategy in enumerate(self._gamesSendingStrategies):
            strategy.sendData(self._internalCommunication, header, gameEntries)
        accumulatedBatches.resetAccumulatedGames()

    def handleReviews(self, accumulatedBatches: AccumulatedBatches, tag: int, header: HeaderInterface, data: bytes):
        reviewEntries = self._reviewsEntry.deserialize(data)
        positiveReviewEntries, negativeReviewEntries = self.separatePositiveAndNegative(reviewEntries)
        accumulatedBatches.accumulateReviews(tag, positiveReviewEntries, negativeReviewEntries, header)
        if accumulatedBatches.shouldSendReviews():
            self.sendReviews(accumulatedBatches)
            return True
        return False
    
    def sendReviews(self, accumulatedBatches):
        if not accumulatedBatches.reviewsToAck():
            return
        header, positiveReviewEntries, negativeReviewEntries = accumulatedBatches.getReviews()
        toSend = [positiveReviewEntries, negativeReviewEntries, negativeReviewEntries]
        for index, strategy in enumerate(self._reviewsSendingStrategies):
            strategy.sendData(self._internalCommunication, header, toSend[index])
        accumulatedBatches.resetAccumulatedReviews()

    def handleDataMessage(self, body, tag):
        header, data = self._headerType.deserialize(body)
        if header.getFragmentNumber() % PRINT_FREQUENCY == 0 or header.getFragmentNumber() == 1:
            logging.info(f'action: received msg corresponding to table {header.getTable()} | {header}')

        if header.getClient() not in self._accumulatedBatchesByID:
            self._accumulatedBatchesByID[header.getClient()] = AccumulatedBatches(header.getClient())
        accumulatedBatches = self._accumulatedBatchesByID[header.getClient()]

        if accumulatedBatches.isPacketDuplicate(header):
            self._internalCommunication.ackAll([tag])
            return

        if header.isGamesTable():
            sentGames = self.handleGames(accumulatedBatches, tag, header, data)
            if sentGames:
                accumulatedBatches.storeMetadata()
                self._internalCommunication.ackAll(accumulatedBatches.consumeGamesToAck())
        elif header.isReviewsTable():
            sentReviews = self.handleReviews(accumulatedBatches, tag, header, data)
            if sentReviews:
                accumulatedBatches.storeMetadata()
                self._internalCommunication.ackAll(accumulatedBatches.consumeReviewsToAck())
        else:
            raise ValueError("Table is not one of the two allowed tables")
        
        self._accumulatedBatchesByID[header.getClient()] = accumulatedBatches
        if not self.reachedCapacity():
            return

        logging.info(f'action: reached full capacity, sending all accumulated batches')
        self.sendGames(accumulatedBatches)
        self.sendReviews(accumulatedBatches)
        accumulatedBatches.storeMetadata()
        self._internalCommunication.ackAll(accumulatedBatches.consumePacketsToAck())
        self._accumulatedBatchesByID[header.getClient()] = accumulatedBatches

    def handleMessage(self, ch, method, _properties, body):
        msgType, msg = InternalMessageType.deserialize(body)
        match msgType:
            case InternalMessageType.DATA_TRANSFER:
                self.handleDataMessage(msg, method.delivery_tag)
            case InternalMessageType.CLIENT_FLUSH:
                # only to games receivers, as they all end up in the same place -> a joiner
                for strategy in self._gamesSendingStrategies:
                    strategy.sendFlush(middleware=self._internalCommunication, clientId=msg)
                ch.basic_ack(delivery_tag = method.delivery_tag)

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)