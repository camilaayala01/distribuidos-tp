import logging
from entryParsing.common.header import Header
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.entry import EntryInterface
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.utils import getEntryTypeFromEnv, getHeaderTypeFromEnv, initializeLog
from .activeClient import ActiveClient
from .joinerConsolidatorTypes import JoinerConsolidatorType
import os
from sendingStrategy.common.utils import createStrategiesFromNextNodes

PRINT_FREQUENCY = 500

class JoinerConsolidator:
    def __init__(self): 
        initializeLog()
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'))
        self._priorNodeCount = int(os.getenv('PRIOR_NODE_COUNT'))
        self._activeClients = {}
        self._currentClient =  None
        self._entryType = getEntryTypeFromEnv()
        self._headerType = getHeaderTypeFromEnv()
        self._consolidatorType  = JoinerConsolidatorType(int(os.getenv('JOINER_CONSOLIDATOR_TYPE')))
        self._sendingStrategies = createStrategiesFromNextNodes()
    
    def stop(self, _signum, _frame):
        self._internalCommunication.stop()

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def _sendToNext(self, batch: list[EntryInterface], clientId: bytes):
        for strategy in self._sendingStrategies:
            newHeader = self._consolidatorType.getResultingHeader(self.getHeader(clientId))
            strategy.send(self._internalCommunication, newHeader, batch)

    def getHeader(self, clientId: bytes):
        return Header(clientId=clientId, fragment=self._currentClient._fragment, eof=self._currentClient.isDone())
    
    def setCurrentClient(self, clientID: bytes):
        self._currentClient = self._activeClients.setdefault(clientID, ActiveClient(self._priorNodeCount))
    
    def shouldSendPackets(self, toSend: list[EntryInterface]):
        return (self._currentClient.isDone() or 
                (not self._currentClient.isDone() and len(toSend) != 0))

    def handleMessage(self, ch, method, properties, body):
        header, data = HeaderWithSender.deserialize(body)
        clientId = header.getClient()
        self.setCurrentClient(clientId)
        if header.getFragmentNumber() % PRINT_FREQUENCY == 0:                
            logging.info(f'action: receiving batch | {header} | result: success')

        if self._currentClient.isDuplicate(header):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
        batch = self._entryType.deserialize(data)
        self._currentClient.update(header)
        
        if self.shouldSendPackets(data):
            self._sendToNext(batch, header.getClient())
            self._currentClient._fragment += 1

        self._activeClients[clientId] = self._currentClient

        if self._currentClient.isDone():
            logging.info(f'action: finished receiving data from client {clientId}| result: success')
            self._activeClients.pop(clientId)
        
        ch.basic_ack(delivery_tag = method.delivery_tag)

