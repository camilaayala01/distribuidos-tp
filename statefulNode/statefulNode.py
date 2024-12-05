from abc import ABC, abstractmethod
import csv
import os
import time
from uuid import UUID
import uuid
from entryParsing.common.fieldLen import CLIENT_ID_LEN
from entryParsing.common.fieldParsing import deserializeBoolean, getClientIdUUID
from entryParsing.common.utils import initializeLog, nextRow
from healthcheckAnswerController.healthcheckAnswerController import HealthcheckAnswerController
from internalCommunication.common.utils import createStrategiesFromNextNodes
from internalCommunication.internalCommunication import InternalCommunication
from internalCommunication.internalMessageType import InternalMessageType
from packetTracker.tracker import TrackerInterface

PRINT_FREQUENCY = 1000
DELETE_TIMEOUT = 20

class StatefulNode(ABC):
    def __init__(self):
        initializeLog()
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'), os.getenv('NODE_ID'))
        self._sendingStrategies = createStrategiesFromNextNodes()
        self._deletedClients = {} # client id: timestamp of the first time flush was seen
        self._activeClients = {}
        self._currentClient = None
        self._healthcheckAnswerController = HealthcheckAnswerController()
        self._healthcheckAnswerController.execute()      
    
    @abstractmethod
    def createClient(self, filepath: str, clientId: UUID, tracker: TrackerInterface):
        pass
    
    @abstractmethod
    def createTrackerFromRow(self, row):
        pass
    
    def loadActiveClientsFromDisk(self):
        dataDirectory = f"/{os.getenv('LISTENING_QUEUE')}/clientData/"
        if not os.path.exists(dataDirectory) or not os.path.isdir(dataDirectory):
            return
        
        for filename in os.listdir(dataDirectory):
            path = os.path.join(dataDirectory, filename)
            if not os.path.isfile(path): 
                continue
            
            if path.endswith('.tmp'):
                os.remove(path)
                continue
            elif path.endswith('.csv'):
                with open(path, 'r') as file:
                    reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
                    packetTrackerRow = nextRow(reader)
                tracker = self.createTrackerFromRow(packetTrackerRow)
                clientUUID = uuid.UUID(filename.removesuffix('.csv'))
                self._activeClients[clientUUID.bytes] = self.createClient(path, clientUUID, tracker)

    def deleteIsEmpty(self):
        return len(self._deletedClients) == 0
        
    def stop(self, _signum, _frame):
        for client in self._activeClients.values():
            client.destroy()
        self._internalCommunication.stop()
        self._healthcheckAnswerController.stop()
        
    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    @abstractmethod
    def setCurrentClient(self, clientId: bytes):
        pass
   
    def handleFlushQueuingAndPropagation(self, clientToRemove, tag, channel, propagate):
        if clientToRemove in self._deletedClients:
            if time.perf_counter() - self._deletedClients[clientToRemove] > DELETE_TIMEOUT:
                print(f"flush for {getClientIdUUID(clientToRemove)} is done")
                channel.basic_ack(delivery_tag = tag)
                self._deletedClients.pop(clientToRemove, None)
            else:
                self._internalCommunication.requeuePacket(tag)
        else:
            self._deletedClients[clientToRemove] = time.perf_counter()
            if not propagate:
                self._internalCommunication.requeuePacket(tag)
                return
            self._internalCommunication.sendFlushToSelf(clientToRemove)
            for strategy in self._sendingStrategies:
                strategy.sendFlush(middleware=self._internalCommunication, clientId=clientToRemove)
            channel.basic_ack(delivery_tag=tag)

    def deleteAccumulated(self, _clientToRemove):
        return
    
    def handleClientFlush(self, clientToRemove, tag, channel, propagate):
        if self._currentClient and clientToRemove == self._currentClient.getClientIdBytes():
            self._currentClient = None
        self.deleteAccumulated(clientToRemove)
        if clientToRemove in self._activeClients:
            client = self._activeClients.pop(clientToRemove)
            client.destroy()
            
        self.handleFlushQueuingAndPropagation(clientToRemove, tag, channel, propagate)
        
    @abstractmethod
    def processDataPacket(self, header, batch, tag, channel):
        pass
        
    def handleDataMessage(self, channel, tag, body):
        header, batch = self._headerType.deserialize(body)
        clientId = header.getClient()
    
        if clientId in self._deletedClients:
            channel.basic_ack(delivery_tag=tag)
            return

        receivedClient = self._activeClients.get(clientId)
        if receivedClient and receivedClient.isDuplicate(header):
            channel.basic_ack(delivery_tag=tag)
            return
        
        self.setCurrentClient(clientId)
        self.processDataPacket(header, batch, tag, channel)
        

    def handleMessage(self, ch, method, _properties, body):
        msgType, msg = InternalMessageType.deserialize(body)
        match msgType:
            case InternalMessageType.DATA_TRANSFER:
                self.handleDataMessage(channel=ch, tag=method.delivery_tag, body=msg)
            case InternalMessageType.CLIENT_FLUSH:
                propagate, _ = deserializeBoolean(CLIENT_ID_LEN, msg)
                self.handleClientFlush(clientToRemove=msg[:CLIENT_ID_LEN], tag=method.delivery_tag, channel=ch, propagate=propagate)