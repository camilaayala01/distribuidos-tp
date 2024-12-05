import csv
import logging
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

PRINT_FREQUENCY = 1000

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
    
    def loadActiveClientsFromDisk(self):
        dataDirectory = f"/{os.getenv('LISTENING_QUEUE')}/"
        if not os.path.exists(dataDirectory) or not os.path.isdir(dataDirectory):
            return
        
        for dirname in os.listdir(dataDirectory):
            path = os.path.join(dataDirectory, dirname)
            
            filepaths = {os.path.join(path, filename) for filename in os.listdir(path)}
            clientUUID = uuid.UUID(dirname)
            tracker = DefaultTracker()
            
            if path + '/games.csv' in filepaths:
                print(f"loading games from storage {clientUUID}")
                gamesTracker = self.loadTrackerFromFile(path + '/games.csv')  
                print(gamesTracker)              
                filepaths.remove(path + '/games.csv')
            
            if path + '/joined.csv' in filepaths:
                print("loading joined from storage")
                reviewsTracker = self.loadTrackerFromFile(path + '/joined.csv')
                print(reviewsTracker) 
                filepaths.remove(path + '/joined.csv')
            elif path + '/reviews.csv' in filepaths:
                print("loading reviews from storage")
                reviewsTracker = self.loadTrackerFromFile(path + '/reviews.csv')
                print(reviewsTracker) 
                filepaths.remove(path + '/reviews.csv')
                    
            self._activeClients[clientUUID.bytes] = self.createClient(clientUUID, gamesTracker, reviewsTracker)
            for filepath in filepaths:
                os.remove(filepath)

    def handleDataMessage(self, body, tag):
        header, data = self._headerType.deserialize(body)
        if header.getFragmentNumber() % PRINT_FREQUENCY == 0 or header.getFragmentNumber() == 1:
            logging.info(f'action: received msg corresponding to table {header.getTable()} | {header}')

        if header.getFragmentNumber() == 1:
            self._accumulatedBatchesByID[header.getClient()] = AccumulatedBatches()

        accumulatedBatches = self._accumulatedBatchesByID[header.getClient()]

        if header.isGamesTable():
            gameEntries = self._gamesEntry.deserialize(data)
            accumulatedBatches.accumulateGames(tag, gameEntries, header.isEOF())
            if accumulatedBatches.shouldSend():
                gameEntries = accumulatedBatches.getGames()
                header._fragment = accumulatedBatches.getFragment()
                for index, strategy in enumerate(self._gamesSendingStrategies):
                    strategy.sendData(self._internalCommunication, header, gameEntries)
                accumulatedBatches.resetAccumulatedGames()
                self._internalCommunication.ackAll(accumulatedBatches.toAck())
        elif header.isReviewsTable():
            reviewEntries = self._reviewsEntry.deserialize(data)
            positiveReviewEntries, negativeReviewEntries = self.separatePositiveAndNegative(reviewEntries)
            accumulatedBatches.accumulateReviews(tag, positiveReviewEntries, negativeReviewEntries, header.isEOF())
            if accumulatedBatches.shouldSend():
                positiveReviewEntries, negativeReviewEntries = accumulatedBatches.getReviews()
                header._fragment = accumulatedBatches.getFragment()
                toSend = [positiveReviewEntries, negativeReviewEntries, negativeReviewEntries]
                for index, strategy in enumerate(self._reviewsSendingStrategies):
                    strategy.sendData(self._internalCommunication, header, toSend[index])
                accumulatedBatches.resetAccumulatedReviews()
                self._internalCommunication.ackAll(accumulatedBatches.toAck())
        else:
            raise ValueError("Table is not one of the two allowed tables")
        
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