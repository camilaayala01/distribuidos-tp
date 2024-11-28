import os
from entryParsing.common.fieldParsing import getClientIdUUID
from healthcheckAnswerController.healthcheckAnswerController import HealthcheckAnswerController
from statefulNode.statefulNode import StatefulNode
from .activeClient import ActiveClient
from entryParsing.common.header import Header
from entryParsing.common.headerInterface import HeaderInterface
from entryParsing.entry import EntryInterface
from .aggregatorTypes import AggregatorTypes
from entryParsing.common.utils import getEntryTypeFromEnv, getHeaderTypeFromEnv

class Aggregator(StatefulNode):
    def __init__(self):
        super().__init__()
        self._aggregatorType = AggregatorTypes(int(os.getenv('AGGREGATOR_TYPE')))
        self._entryType = getEntryTypeFromEnv()
        self._headerType = getHeaderTypeFromEnv()  

    def sendToNext(self, header: HeaderInterface, entries: list[EntryInterface]):
        for strategy in self._sendingStrategies:
            strategy.sendData(self._internalCommunication, header, entries)

    def getHeader(self, clientId: bytes):
        return Header(_clientId=clientId, _fragment=self._currentClient._fragment, _eof=self._currentClient.finishedReceiving())

    def shouldSendPackets(self, toSend: list[EntryInterface]):
        return self._currentClient.finishedReceiving() or (not self._currentClient.finishedReceiving() and len(toSend) != 0)
    
    def handleSending(self, ready: list[EntryInterface], clientId):
        header = self._aggregatorType.getResultingHeader(self.getHeader(clientId))
        if self.shouldSendPackets(ready):
            self.sendToNext(header, ready)
            # TODO write fragment in file
            self._currentClient._fragment += 1
        self._activeClients[clientId] = self._currentClient

        if self._currentClient.finishedReceiving():
            self._activeClients.pop(clientId).destroy()

    def setCurrentClient(self, clientId: bytes):
        self._currentClient = self._activeClients.setdefault(clientId, 
                                                             ActiveClient(getClientIdUUID(clientId), 
                                                                          self._aggregatorType.getInitialResults(), 
                                                                          self._aggregatorType.initializeTracker(clientId)))
        
    def processDataPacket(self, header, batch, tag, channel):
        clientId = header.getClient()
        self._currentClient.update(header)
        entries = self._entryType.deserialize(batch)
        path = self._currentClient.partialResPath()
        toSend = self._aggregatorType.handleResults(entries, self._entryType, path, self._currentClient.finishedReceiving())
        self.handleSending(toSend, clientId)
        channel.basic_ack(delivery_tag = tag)