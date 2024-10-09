from abc import ABC, abstractmethod
import logging
import signal
from entryParsing.common.header import Header
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.entry import EntryInterface
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.utils import initializeLog
from packetTracker.multiTracker import MultiTracker

class JoinerConsolidator(ABC):
    def __init__(self, type: str, nextNodeCount: int, priorNodeCount: int, entriesType: EntryInterface): 
        initializeLog()
        self._internalCommunication = InternalCommunication(type, None)
        self._entriesType = entriesType
        self._tracker = MultiTracker(priorNodeCount)
        self._nextNodeCount = nextNodeCount
        self._priorNodeCount = priorNodeCount
        self._currFragment = 1
    
    def stop(self, _signum, _frame):
        self._internalCommunication.stop()

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)
        
    def reset(self):
        self._tracker.reset()
        self._currFragment = 1

    def getHeaderSerialized(self):
        return Header(fragment=self._currFragment, eof=self._tracker.isDone()).serialize()

    @abstractmethod
    def handleSending(self, header: HeaderWithSender, data: bytes):
        pass

    def handleMessage(self, ch, method, properties, body):
        header, data = HeaderWithSender.deserialize(body)
        logging.info(f'action: received batch | {header} | result: success')
        if self._tracker.isDuplicate(header):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
        self._tracker.update(header)

        if self._tracker.isDone() or (not self._tracker.isDone() and not len(data) == 0):
            self.handleSending(header, data)
            self._currFragment += 1
        
        if self._tracker.isDone():
            self.reset()
        
        ch.basic_ack(delivery_tag = method.delivery_tag)

