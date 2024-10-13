import logging
from entryParsing.common.header import Header
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.entry import EntryInterface
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.utils import initializeLog
from .joinerConsolidatorTypes import JoinerConsolidatorType
from packetTracker.multiTracker import MultiTracker
import os
from sendingStrategy.common.utils import createStrategiesFromNextNodes

PRINT_FREQUENCY = 51

class JoinerConsolidator:
    def __init__(self): 
        initializeLog()
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'))
        self._priorNodeCount = int(os.getenv('PRIOR_NODE_COUNT'))
        self._tracker = MultiTracker(self._priorNodeCount)
        self._consolidatorType  = JoinerConsolidatorType(int(os.getenv('JOINER_CONSOLIDATOR_TYPE')))
        self._sendingStrategies = createStrategiesFromNextNodes()
        self._currFragment = 1
    
    def stop(self, _signum, _frame):
        self._internalCommunication.stop()

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)
        
    def reset(self):
        self._tracker.reset()
        self._currFragment = 1

    def _sendToNext(self, batch: list[EntryInterface]):
        for strategy in self._sendingStrategies:
            newHeader = self._consolidatorType.getResultingHeader(self.getHeader())
            strategy.send(self._internalCommunication, newHeader, batch)

    def getHeader(self):
        return Header(fragment=self._currFragment, eof=self._tracker.isDone())

    def handleMessage(self, ch, method, properties, body):
        header, data = HeaderWithSender.deserialize(body)
        if header.getFragmentNumber() % PRINT_FREQUENCY == 0:                
            logging.info(f'action: receiving batch | {header} | result: success')

        batch = self._consolidatorType.entryType().deserialize(data)
        if self._tracker.isDuplicate(header):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
        
        self._tracker.update(header)
        
        if self._tracker.isDone() or (not self._tracker.isDone() and not len(data) == 0):
            self._sendToNext(batch)
            self._currFragment += 1
        
        if self._tracker.isDone():
            self.reset()
        
        ch.basic_ack(delivery_tag = method.delivery_tag)

