import os
import logging
import time
from entryParsing.common.fieldParsing import getClientIdUUID
from entryParsing.common.header import Header
from entryParsing.common.headerInterface import HeaderInterface
from entryParsing.entry import EntryInterface
from internalCommunication.internalCommunication import InternalCommunication
from internalCommunication.internalMessageType import InternalMessageType
from .activeClient import ActiveClient
from .aggregatorTypes import AggregatorTypes
from entryParsing.common.utils import getEntryTypeFromEnv, getHeaderTypeFromEnv, initializeLog
from internalCommunication.common.utils import createStrategiesFromNextNodes

PRINT_FREQ = 1000
DELETE_TIMEOUT = 5

class Aggregator:
    def __init__(self):
        initializeLog()
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'), os.getenv('NODE_ID'))
        self._aggregatorType = AggregatorTypes(int(os.getenv('AGGREGATOR_TYPE')))
        self._entryType = getEntryTypeFromEnv()
        self._headerType = getHeaderTypeFromEnv() 
        self._sendingStrategies = createStrategiesFromNextNodes()
        self._activeClients = {}
        self._deletedClients = {} # client id: timestamp of the first time flush was seen
        self._currentClient = None
        

    def stop(self, _signum, _frame):
        for client in self._activeClients.values():
            client.destroy()
        self._internalCommunication.stop()

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def setCurrentClient(self, clientId: bytes):
        self._currentClient = self._activeClients.setdefault(clientId, 
                                                             ActiveClient(getClientIdUUID(clientId), 
                                                                          self._aggregatorType.getInitialResults(), 
                                                                          self._aggregatorType.initializeTracker(clientId)))

    def _sendToNext(self, header: HeaderInterface, entries: list[EntryInterface]):
        for strategy in self._sendingStrategies:
            strategy.sendData(self._internalCommunication, header, entries)

    def shouldSendPackets(self, toSend: list[EntryInterface]):
        return self._currentClient.isDone() or (not self._currentClient.isDone() and len(toSend) != 0)
    
    def getHeader(self, clientId: bytes):
        return Header(_clientId=clientId, _fragment=self._currentClient._fragment, _eof=self._currentClient.isDone())

    def _handleSending(self, ready: list[EntryInterface], clientId):
        header = self._aggregatorType.getResultingHeader(self.getHeader(clientId))
        if self.shouldSendPackets(ready):
            self._sendToNext(header, ready)
            # TODO write fragment in file
            self._currentClient._fragment += 1
            
        self._activeClients[clientId] = self._currentClient

        if self._currentClient.isDone():
            self._activeClients.pop(clientId).destroy()

    def handleDataMessage(self, channel, tag, body):
        header, data = self._headerType.deserialize(body)
        clientId = header.getClient()
        if clientId in self._deletedClients:
            print("received packet from deleted client lol")
            channel.basic_ack(delivery_tag = tag)
            return
        self.setCurrentClient(header.getClient())
        if header.getFragmentNumber() % PRINT_FREQ == 0:
            logging.info(f'action: received batch | {header} | result: success')
        
        if self._currentClient.isDuplicate(header):
            channel.basic_ack(delivery_tag = tag)
            return
        self._currentClient.update(header)
        entries = self._entryType.deserialize(data)
        path = self._currentClient.partialResPath()
        toSend = self._aggregatorType.handleResults(entries, self._entryType, path, self._currentClient.isDone())
        self._handleSending(toSend, clientId)
        channel.basic_ack(delivery_tag = tag)

    def handleFlushQueuingAndPropagation(self, clientToRemove, tag, channel):
        if clientToRemove in self._deletedClients:
            if time.perf_counter() - self._deletedClients[clientToRemove] > DELETE_TIMEOUT:
                channel.basic_ack(delivery_tag = tag)
                self._deletedClients.pop(clientToRemove, None)
            else: 
                self._internalCommunication.requeuePacket(tag)
        else:
            self._deletedClients[clientToRemove] = time.perf_counter()
            self._internalCommunication.requeuePacket(tag)
            for strategy in self._sendingStrategies:
                strategy.sendFlush(middleware=self._internalCommunication, clientId=clientToRemove)
    
    """
    returns true if it ended flush forever and packet can be safely acked
    returns false if it should requeue it cause timeout is not done
    """
    def handleClientFlush(self, clientToRemove, tag, channel):
        if self._currentClient and clientToRemove == self._currentClient.getClientIdBytes():
            self._currentClient = None

        if clientToRemove in self._activeClients:
            client = self._activeClients.pop(clientToRemove)
            client.destroy()
            
        self.handleFlushQueuingAndPropagation(clientToRemove, tag, channel)

    def handleMessage(self, ch, method, _properties, body):
        msgType, msg = InternalMessageType.deserialize(body)
        match msgType:
            case InternalMessageType.DATA_TRANSFER:
                self.handleDataMessage(channel=ch, tag=method.delivery_tag, body=msg)
            case InternalMessageType.CLIENT_FLUSH:
                self.handleClientFlush(clientToRemove=msg, tag=method.delivery_tag, channel=ch)
        