from abc import ABC, abstractmethod
import logging
import os
import time
from entryParsing.common.fieldParsing import getClientIdUUID
from entryParsing.common.utils import initializeLog
from internalCommunication.common.utils import createStrategiesFromNextNodes
from internalCommunication.internalCommunication import InternalCommunication
from internalCommunication.internalMessageType import InternalMessageType

PRINT_FREQUENCY = 1000
DELETE_TIMEOUT = 5

class StatefulNode(ABC):
    def __init__(self):
        initializeLog()
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'), os.getenv('NODE_ID'))
        self._sendingStrategies = createStrategiesFromNextNodes()
        self._deletedClients = {} # client id: timestamp of the first time flush was seen
        self._activeClients = {}
        self._currentClient = None
    
    def deleteIsEmpty(self):
        return len(self._deletedClients) == 0
    
    def stop(self, _signum, _frame):
        for client in self._activeClients.values():
            client.destroy()
        self._internalCommunication.stop()
        
    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    @abstractmethod
    def setCurrentClient(self, clientId: bytes):
        pass
   
    def handleFlushQueuingAndPropagation(self, clientToRemove, tag, channel):
        if clientToRemove in self._deletedClients:
            if time.perf_counter() - self._deletedClients[clientToRemove] > DELETE_TIMEOUT:
                print(f"flush for {getClientIdUUID(clientToRemove)} is done")
                channel.basic_ack(delivery_tag = tag)
                self._deletedClients.pop(clientToRemove, None)
            else:
                self._internalCommunication.requeuePacket(tag)
        else:
            print(f"received flush for {getClientIdUUID(clientToRemove)} is done")
            self._deletedClients[clientToRemove] = time.perf_counter()
            self._internalCommunication.requeuePacket(tag)
            for strategy in self._sendingStrategies:
                strategy.sendFlush(middleware=self._internalCommunication, clientId=clientToRemove)

    def deleteAccumulated(self, _clientToRemove):
        return
    
    def handleClientFlush(self, clientToRemove, tag, channel):
        if self._currentClient and clientToRemove == self._currentClient.getClientIdBytes():
            self._currentClient = None
        self.deleteAccumulated(clientToRemove)
        if clientToRemove in self._activeClients:
            client = self._activeClients.pop(clientToRemove)
            print(f"deleting {client._clientId}")
            client.destroy()
            
        self.handleFlushQueuingAndPropagation(clientToRemove, tag, channel)
        
    @abstractmethod
    def processDataPacket(self, header, batch, tag, channel):
        pass
        
    def handleDataMessage(self, channel, tag, body):
        header, batch = self._headerType.deserialize(body)
        clientId = header.getClient()
        self.setCurrentClient(clientId)

        if clientId in self._deletedClients:
            channel.basic_ack(delivery_tag=tag)
            return

        receivedClient = self._activeClients.get(clientId)
        if receivedClient and receivedClient.isDuplicate(header):
            channel.basic_ack(delivery_tag=tag)
            return
        
        self.processDataPacket(header, batch, tag, channel)

    def handleMessage(self, ch, method, _properties, body):
        msgType, msg = InternalMessageType.deserialize(body)
        match msgType:
            case InternalMessageType.DATA_TRANSFER:
                self.handleDataMessage(channel=ch, tag=method.delivery_tag, body=msg)
            case InternalMessageType.CLIENT_FLUSH:
                self.handleClientFlush(clientToRemove=msg, tag=method.delivery_tag, channel=ch)