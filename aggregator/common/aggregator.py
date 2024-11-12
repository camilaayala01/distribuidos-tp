import os
import logging
from entryParsing.common.fieldParsing import getClientIdUUID
from entryParsing.common.header import Header
from entryParsing.common.headerInterface import HeaderInterface
from entryParsing.entry import EntryInterface
from internalCommunication.internalCommunication import InternalCommunication
from .activeClient import ActiveClient
from .aggregatorTypes import AggregatorTypes
from entryParsing.common.utils import getEntryTypeFromEnv, getHeaderTypeFromEnv, initializeLog
from internalCommunication.common.utils import createStrategiesFromNextNodes

PRINT_FREQ = 1000

class Aggregator:
    def __init__(self):
        initializeLog()
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'), os.getenv('NODE_ID'))
        self._aggregatorType = AggregatorTypes(int(os.getenv('AGGREGATOR_TYPE')))
        self._entryType = getEntryTypeFromEnv()
        self._headerType = getHeaderTypeFromEnv() 
        self._sendingStrategies = createStrategiesFromNextNodes()
        self._activeClients = {}
        self._currentClient = None

    def stop(self, _signum, _frame):
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
            strategy.send(self._internalCommunication, header, entries)

    def shouldSendPackets(self, toSend: list[EntryInterface]):
        return self._currentClient.isDone() or (not self._currentClient.isDone() and len(toSend) != 0)
    
    def getHeader(self, clientId: bytes):
        return Header(_clientId=clientId, _fragment=self._currentClient._fragment, _eof=self._currentClient.isDone())

    def _handleSending(self, ready: list[EntryInterface], clientId):
        header = self._aggregatorType.getResultingHeader(self.getHeader(clientId))
        if self.shouldSendPackets(ready):
            self._sendToNext(header, ready)
            self._currentClient._fragment += 1 #write
            
        self._activeClients[clientId] = self._currentClient

        if self._currentClient.isDone():
            self._activeClients.pop(clientId).destroy()


    def handleMessage(self, ch, method, _properties, body):
        header, data = self._headerType.deserialize(body)
        clientId = header.getClient()
        self.setCurrentClient(header.getClient())
        if header.getFragmentNumber() % PRINT_FREQ == 0:
            logging.info(f'action: received batch | {header} | result: success')
        
        if self._currentClient.isDuplicate(header):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
        self._currentClient.update(header)
        entries = self._entryType.deserialize(data)
        path = self._currentClient.partialResPath()
        toSend = self._aggregatorType.handleResults(entries, self._entryType, path, self._currentClient.isDone())
        self._handleSending(toSend, clientId)
        ch.basic_ack(delivery_tag = method.delivery_tag)