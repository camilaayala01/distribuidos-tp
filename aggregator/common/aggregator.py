import csv
import os
from uuid import UUID
from entryParsing.common.fieldParsing import getClientIdUUID, serializeBoolean
from internalCommunication.internalMessageType import InternalMessageType
from packetTracker.tracker import TrackerInterface
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
        self.loadActiveClientsFromDisk()
    
    def createTrackerFromRow(self, row):
        return self._aggregatorType.trackerType().fromStorage(row)
    
    def createClient(self, filepath: str, clientId: UUID, tracker: TrackerInterface):
        client = ActiveClient(clientId=clientId, tracker=tracker)
        client.loadFragment(filepath=filepath)
        return client

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
            self._currentClient._fragment += 1
        self._activeClients[clientId] = self._currentClient
        self._currentClient.saveNewResults()

        if self._currentClient.finishedReceiving():
            self._internalCommunication.basicSend(self._internalCommunication.getQueueName(), InternalMessageType.CLIENT_FLUSH.serialize() + clientId + serializeBoolean(False))

    def setCurrentClient(self, clientId: bytes):
        trackerType = self._aggregatorType.trackerType()
        self._currentClient = self._activeClients.setdefault(clientId, 
                                                             ActiveClient(getClientIdUUID(clientId),
                                                                          trackerType()))

    def persistNewData(self, entries):
        toSend = []
        with open(self._currentClient.storagePath() + '.tmp', 'w+') as file:
            self._currentClient.storeTracker(file)
            toSend = self._aggregatorType.handleResults(entries, 
                                                        self._currentClient.loadEntries(self._entryType), 
                                                        file, 
                                                        self._currentClient.finishedReceiving())
            self._currentClient.storeFragment(file, self.shouldSendPackets(toSend))
        return toSend

    def processDataPacket(self, header, batch, tag, channel):
        clientId = header.getClient()
        self._currentClient.update(header)
        entries = self._entryType.deserialize(batch)
        toSend = self.persistNewData(entries)
        self.handleSending(toSend, clientId)
        channel.basic_ack(delivery_tag = tag)
