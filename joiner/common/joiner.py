from collections import defaultdict
import csv
import logging
import os
import uuid
from entryParsing.common.fieldParsing import getClientIdUUID
from entryParsing.common.utils import getGamesEntryTypeFromEnv, getHeaderTypeFromEnv, getReviewsEntryTypeFromEnv, nextRow
from entryParsing.messagePart import MessagePartInterface
from eofController.eofController import EofController
from packetTracker.defaultTracker import DefaultTracker
from statefulNode.statefulNode import StatefulNode
from .accumulatedBatches import AccumulatedBatches
from .activeClient import ActiveClient
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
        client = ActiveClient(clientId=clientId, gamesTracker=gamesTracker, reviewsTracker=reviewsTracker)
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
                gamesTracker = self.loadTrackerFromFile(path + '/games.csv')                
                filepaths.remove(path + '/games.csv')
            
            if path + '/joined.csv' in filepaths:
                reviewsTracker = self.loadTrackerFromFile(path + '/joined.csv')
                filepaths.remove(path + '/joined.csv')
            elif path + '/reviews.csv' in filepaths:
                reviewsTracker = self.loadTrackerFromFile(path + '/reviews.csv')
                filepaths.remove(path + '/reviews.csv')
                    
            self._activeClients[clientUUID.bytes] = self.createClient(clientUUID, gamesTracker, reviewsTracker)
            for filepath in filepaths:
                os.remove(filepath)

    """keeps the client if there is one, set a new one if there's not"""
    def setCurrentClient(self, clientId: bytes):
        if self._currentClient:
            return
        self._currentClient = self._activeClients.setdefault(clientId, ActiveClient(getClientIdUUID(clientId), DefaultTracker(), DefaultTracker()))
    
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
        return joinedEntries
        
    def handleReviewsMessage(self, data: bytes):
        reviews = self._reviewsEntry.deserialize(data)
        if not self._currentClient.isGamesDone():
            if reviews:
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
        accumulator = AccumulatedBatches(header.getClient())
        accumulator.accumulate(tag, header, batch)
        self._accumulatedBatches = accumulator

    def processPendingBatches(self):
        self.handleGamesMessage(self._accumulatedBatches.getGamesBatches())
        joinedEntries = self.handleReviewsMessage(self._accumulatedBatches.getReviewsBatches())

        self.handleSending(joinedEntries)

        if self._currentClient.isGamesDone():
            self._currentClient.storeFragment()
            self._currentClient.saveNewResults(self._currentClient.joinedPath())
            self._currentClient.removeUnjoinedReviews() 

        toAck = self._accumulatedBatches.toAck()
        self._activeClients[self._accumulatedBatches._clientId] = self._currentClient
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

        if not self.shouldProcessAccumulated():
            self._activeClients[self._accumulatedBatches.getClient()] = self._currentClient
            return

        self._internalCommunication.ackAll(self.processPendingBatches())

        if self._currentClient.finishedReceiving():
            logging.info(f'action: finished receiving data from client {getClientIdUUID(clientId)}| result: success')
            self._eofController.finishedProcessing(self._currentClient._fragment, clientId, self._internalCommunication)
            self._currentClient = None
            self._activeClients.pop(clientId).destroy()
