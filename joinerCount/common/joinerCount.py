import os
import logging
from entryParsing.common.header import Header
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.entryOSCount import EntryOSCount
from internalCommunication.internalCommunication import InternalCommunication
from .joinerCountType import JoinerCountType
from packetTracker.defaultTracker import DefaultTracker
from sendingStrategy.common.utils import createStrategiesFromNextNodes

"""
Joins counts 
"""
class JoinerCount:
    def __init__(self):
        self._packetTracker = DefaultTracker()
        self._joinerType = JoinerCountType(int(os.getenv('JOINER_TYPE')))
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'))
        self._sendingStrategies = createStrategiesFromNextNodes()
        # key: client id, value: counts
        self._counts = {}

    def reset(self):
        self._packetTracker.reset()
             
    def stop(self, _signum, _frame):
        self._internalCommunication.stop()
    
    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def handleMessage(self, ch, method, properties, body):
        logging.info(f'action: receiving batch from grouper OS counts | result: success')
        header, data = self._joinerType.headerType().deserialize(body)
        if self._packetTracker.isDuplicate(header):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
        self._packetTracker.update(header)
        incoming = self._joinerType.entryType().deserialize(data)

        # change '1' for client id
        self._counts['1'] = self._joinerType._applySum(incoming=incoming, prior=self._counts.get('1', self._joinerType.getDefaultEntry()))
        
        logging.info(f'action: joining received batches by supported OS | result: success')
        self._handleSending()
        ch.basic_ack(delivery_tag = method.delivery_tag)
        
    def _sendToNextStep(self, data: bytes):
        self._internalCommunication.sendToDispatcher(data)

    def _handleSending(self):
        if not self._packetTracker.isDone():
            return
        # only one node is in charge of calculating counts, in only one packet 
        # (never 3 numbers and a header will take up more than 4096 bytes)
        headerBytes = HeaderWithQueryNumber(fragment=1, eof=True, queryNumber=1).serialize()
        countsBytes = self._buildResult().serialize()
        self._sendToNextStep(headerBytes + countsBytes)
        logging.info(f'action: sending results to dispatcher | result: success')
        self.reset()

    def _buildResult(self) -> EntryOSCount:
        return EntryOSCount(self._windows, self._mac, self._linux, self._total)