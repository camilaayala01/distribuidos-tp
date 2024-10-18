import os
import logging
from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface
from internalCommunication.internalCommunication import InternalCommunication
from .joinerCountTypes import JoinerCountType
from packetTracker.defaultTracker import DefaultTracker
from entryParsing.common.utils import getEntryTypeFromEnv, initializeLog
from sendingStrategy.common.utils import createStrategiesFromNextNodes

PRINT_FREQ = 100
"""
Entities that join all partial counts and streams results to clients
More than one entity
Query 4
"""

class JoinerCount:
    def __init__(self):
        initializeLog()
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'), os.getenv('NODE_ID'))
        self._joinerCountType = JoinerCountType(int(os.getenv('JOINER_COUNT_TYPE')))
        self._packetTracker = DefaultTracker()
        self._entryType = getEntryTypeFromEnv() 
        self._counts = self._joinerCountType.getInitialResults()
        self._sent = set()
        self._fragnum = 1
        self._sendingStrategies = createStrategiesFromNextNodes()

    def stop(self, _signum, _frame):
        self._internalCommunication.stop()

    def reset(self):
        self._packetTracker.reset()
        self._counts = self._joinerCountType.getInitialResults()
        self._sent = set()
        self._fragnum = 1

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    # should have a fragment number to stream results to client
    def handleMessage(self, ch, method, properties, body):
        header, data = self._joinerCountType.headerType().deserialize(body)
        if header.getFragmentNumber() % PRINT_FREQ == 0:
            logging.info(f'action: received batch | {header} | result: success')
        if self._packetTracker.isDuplicate(header):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
        self._packetTracker.update(header)
        entries = self._entryType.deserialize(data)
        
        toSend, self._counts, self._sent = self._joinerCountType.handleResults(entries, 
                                                                               self._counts, 
                                                                               self._packetTracker.isDone(), 
                                                                               self._sent)
        self._handleSending(toSend)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def _sendToNext(self, header: Header, entries: list[EntryInterface]):
        for strategy in self._sendingStrategies:
            strategy.send(self._internalCommunication, header, entries)

    def shouldSendPackets(self, toSend: list[EntryInterface]):
        return self._packetTracker.isDone() or (not self._packetTracker.isDone() and len(toSend) != 0)
    
    def _handleSending(self, ready: list[EntryInterface]):
        header = self._joinerCountType.getResultingHeader(self._fragnum, self._packetTracker.isDone())
        if self.shouldSendPackets(ready):
            self._sendToNext(header, ready)
            self._fragnum += 1

        if self._packetTracker.isDone():
            self.reset()