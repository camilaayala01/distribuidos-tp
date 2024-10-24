import os
import logging
from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface
from internalCommunication.internalCommunication import InternalCommunication
from .activeClient import ActiveClient
from .joinerCountTypes import JoinerCountType
from entryParsing.common.utils import getEntryTypeFromEnv, getHeaderTypeFromEnv, initializeLog
from sendingStrategy.common.utils import createStrategiesFromNextNodes

PRINT_FREQ = 100

class JoinerCount:
    def __init__(self):
        initializeLog()
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'), os.getenv('NODE_ID'))
        self._joinerCountType = JoinerCountType(int(os.getenv('JOINER_COUNT_TYPE')))
        self._entryType = getEntryTypeFromEnv()
        self._headerType = getHeaderTypeFromEnv() 
        self._sendingStrategies = createStrategiesFromNextNodes()
        self._activeClients = {}
        self._currentClient = None

    def stop(self, _signum, _frame):
        self._internalCommunication.stop()

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def setCurrentClient(self, clientID: bytes):
        self._currentClient = self._activeClients.setdefault(clientID, ActiveClient())
        
    # should have a fragment number to stream results to client
    def handleMessage(self, ch, method, properties, body):
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
        
        toSend, self._currentClient._counts, self._currentClient._sent = self._joinerCountType.handleResults(entries, 
                                                                               self._currentClient._counts, 
                                                                               self._currentClient.isDone(), 
                                                                               self._currentClient._sent)
        self._handleSending(toSend, clientId)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def _sendToNext(self, header: Header, entries: list[EntryInterface]):
        for strategy in self._sendingStrategies:
            strategy.send(self._internalCommunication, header, entries)

    def shouldSendPackets(self, toSend: list[EntryInterface]):
        return self._currentClient.isDone() or (not self._currentClient.isDone() and len(toSend) != 0)
    
    def _handleSending(self, ready: list[EntryInterface], clientId):
        header = self._joinerCountType.getResultingHeader(clientId, self._currentClient._fragment, self._currentClient.isDone())
        if self.shouldSendPackets(ready):
            self._sendToNext(header, ready)
            self._currentClient._fragment += 1
            
        self._activeClients[clientId] = self._currentClient

        if self._currentClient.isDone():
            self._activeClients.pop(clientId)