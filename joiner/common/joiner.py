from collections import defaultdict
import csv
import logging
import os
from entryParsing.common.fieldParsing import getClientIdUUID
import uuid
from entryParsing.common.table import Table
from entryParsing.common.utils import getGamesEntryTypeFromEnv, getHeaderTypeFromEnv, getReviewsEntryTypeFromEnv, nextRow
from entryParsing.messagePart import MessagePartInterface
from eofController.eofController import EofController
from packetTracker.defaultTracker import DefaultTracker
from statefulNode.statefulNode import StatefulNode
from .accumulatedBatches import AccumulatedBatches
from .activeClient import JoinerClient
from .joinerTypes import JoinerType
from statefulNode.statefulNode import StatefulNode
PRINT_FREQUENCY = 1000
PREFETCH_COUNT = int(os.getenv('PREFETCH_COUNT'))


class Joiner(StatefulNode):
    def __init__(self):
        super().__init__()
        self.loadActiveClientsFromDisk()
        self._joinerType = JoinerType(int(os.getenv('JOINER_TYPE')))
        self._gamesEntry = getGamesEntryTypeFromEnv()
        self._reviewsEntry = getReviewsEntryTypeFromEnv()
        self._headerType = getHeaderTypeFromEnv()
        nodeID = os.getenv('NODE_ID')
        self._id = int(nodeID)
        self._eofController = EofController(self._id, os.getenv('LISTENING_QUEUE'), int(os.getenv('NODE_COUNT')), self._sendingStrategies)
        self._eofController.execute()
        self._accumulatedBatches = None

    def stop(self, _signum, _frame):
        self._eofController.terminateProcess(self._internalCommunication)
        super().stop(_signum, _frame)
    
    def createClient(self, clientId: uuid.UUID, gamesTracker: DefaultTracker, reviewsTracker: DefaultTracker):
        client = JoinerClient(clientId=clientId, gamesTracker=gamesTracker, reviewsTracker=reviewsTracker)
        client.loadFragment()
        return client
    
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
            if not os.path.isdir(path): 
                continue
            filepaths = {os.path.join(path, filename) for filename in os.listdir(path)}
            clientUUID = uuid.UUID(dirname)
            gamesTracker, reviewsTracker = DefaultTracker(), DefaultTracker()
            
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

    """keeps the client if there is one, set a new one if there's not"""
    def setCurrentClient(self, clientId: bytes):
        if self._currentClient:
            return
        self._currentClient = self._activeClients.setdefault(clientId, JoinerClient(getClientIdUUID(clientId), DefaultTracker(), DefaultTracker()))
    
    """replaces the old client with a new one"""
    def setNewClient(self, clientId: bytes):
        self._currentClient = None
        self.setCurrentClient(clientId)

    def joinReviews(self, reviews: list[MessagePartInterface]):
        unjoined = list(self._currentClient.loadReviewsEntries(self._reviewsEntry))
        
        reviews.extend(unjoined)
        batch = defaultdict(list)
        
        joinedEntries = {}
        for entry in reviews:
            batch[entry._appID].append(entry)

        generator = self._currentClient.loadGamesEntries(self._gamesEntry)
        for game in generator:
            if not len(batch): # once we joined all reviews available, quit
                break
            id = game._appID
            name = game._name
            if id in batch:
                reviewsWithID = batch.pop(id)
                for review in reviewsWithID:
                    priorJoined =  joinedEntries.get(id, self._joinerType.defaultEntry(name, id))
                    joinedEntries[id] = self._joinerType.applyJoining(id, name, priorJoined, review)
        
        self._currentClient.storeJoinedEntries(self._joinerType.entriesToSave(joinedEntries), self._joinerType.joinedEntryType())
        # print(f"stored tracker {self._currentClient._reviewsTracker}")
        return joinedEntries
        
    def handleReviewsMessage(self, data: bytes):
        reviews = self._reviewsEntry.deserialize(data)
        if not self._currentClient.isGamesDone():
            self._currentClient.storeUnjoinedReviews(reviews)
            return
        return self.joinReviews(reviews) 

    def handleGamesMessage(self, data: bytes):
        entries = self._gamesEntry.deserialize(data)
        self._currentClient.storeGamesEntries(entries)

    def shouldSendPackets(self, toSend):
        return toSend is not None
    
    def handleSending(self, joinedEntries):
        currClient = self._currentClient
        if joinedEntries is None:
            return
        toSend = self._joinerType.entriesToSend(joinedEntries=joinedEntries, 
                                                isDone=currClient.finishedReceiving(),
                                                activeClient=currClient)
        if not self.shouldSendPackets(toSend):
            return
        self.sendToNext(toSend)

    def sendToNext(self, generator):
        for strategy in self._sendingStrategies:
            newFragment = strategy.sendFragmenting(self._internalCommunication, 
                                                   self._currentClient.getClientIdBytes(), 
                                                   self._currentClient._fragment, 
                                                   generator, 
                                                   False,
                                                   _sender = self._id)
        self._currentClient._fragment = newFragment
    
    def setAccumulatedBatches(self, tag, header, batch):
        accumulator = AccumulatedBatches(header.getClient(), header.getTable())
        accumulator.accumulate(tag, header, batch)
        self._accumulatedBatches = accumulator

    def processPendingBatches(self):
        if self._accumulatedBatches.getCorrespondingTable() == Table.GAMES:
            self.handleGamesMessage(self._accumulatedBatches.getPendingBatches())
        else:
            joinedEntries = self.handleReviewsMessage(self._accumulatedBatches.getPendingBatches())

            self.handleSending(joinedEntries)

            if self._currentClient.isGamesDone():
                self._currentClient.storeFragment()
                self._currentClient.saveNewResults(self._currentClient.joinedPath())
                self._currentClient.removeUnjoinedReviews() 

        toAck = self._accumulatedBatches.toAck()
        self._activeClients[self._currentClient.getClientIdBytes()] = self._currentClient
        self._accumulatedBatches = None
        return toAck
    
    def shouldProcessAccumulated(self):
        return self._accumulatedBatches.accumulatedLen() == PREFETCH_COUNT or self._currentClient.finishedReceiving()
    
    def deleteAccumulated(self, clientToRemove):        
        if self._accumulatedBatches and clientToRemove == self._accumulatedBatches.getClient():
            self._internalCommunication.ackAll(self._accumulatedBatches.toAck())
            self._accumulatedBatches = None
           
    def processDataPacket(self, header, batch, tag, channel):
        clientId = header.getClient()
        
        if self._accumulatedBatches is None:
            self.setAccumulatedBatches(tag, header, batch)
        elif not self._accumulatedBatches.accumulate(header=header, tag=tag, batch=batch):
            self._internalCommunication.ackAll(self.processPendingBatches())
            self.setAccumulatedBatches(tag, header, batch) 
            self.setNewClient(clientId)

        self._currentClient.updateTracker(header)
        if header.isGamesTable() and self._currentClient.isGamesDone():
            print(f"just finished processing all games for {header.getClient()}")
        if not self.shouldProcessAccumulated():
            self._activeClients[self._currentClient.getClientIdBytes()] = self._currentClient
            return

        self._internalCommunication.ackAll(self.processPendingBatches())

        if self._currentClient.finishedReceiving():
            logging.info(f'action: finished receiving data from client {getClientIdUUID(clientId)}| result: success')
            self._eofController.finishedProcessing(self._currentClient._fragment, clientId, self._internalCommunication)
            self._currentClient = None
            self._internalCommunication.sendFlushToSelf(clientId)
