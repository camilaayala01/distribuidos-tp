import os
from entryParsing.common.header import Header
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.entryOSCount import EntryOSCount
from internalCommunication.internalCommunication import InternalCommunication
from packetTracker.defaultTracker import DefaultTracker

"""
Just one entity that sums one clients sums
Corresponds to query 1
"""
class JoinerOSCount:
    def __init__(self):
        self._internalComunnication = InternalCommunication(os.getenv('JOIN_OS'))
        self._packetTracker = DefaultTracker()
        self._windows = 0
        self._mac = 0
        self._linux = 0

    def reset(self):
        self._packetTracker.reset()
        self._windows = 0
        self._mac = 0
        self._linux = 0

    def execute(self):
        self._internalComunnication.defineMessageHandler(self.handleMessage())

    def handleMessage(self, ch, method, properties, body):
        header, data = Header.deserialize(body)
        if self._packetTracker.isDuplicate(header):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
        osCount = EntryOSCount.deserialize(data)
        self._sum(osCount)
        self._handleSending()
        ch.basic_ack(delivery_tag = method.delivery_tag)
        
    def _sendToNextStep(self, data: bytes):
        self._internalComunnication.sendToDispatcher(data)

    def _handleSending(self):
        if not self._packetTracker.isDone():
            return
        # only one node is in charge of calculating counts, in only one packet 
        # (never 3 numbers and a header will take up more than 4096 bytes)
        headerBytes = HeaderWithQueryNumber(fragment=1, eof=True, queryNumber=1).serialize()
        countsBytes = self._buildResult().serialize()
        self._sendToNextStep(headerBytes + countsBytes)
        self.reset()

    def _sum(self, entry: EntryOSCount):
        self._windows += entry.getWindowsCount()
        self._mac += entry.getMacCount()
        self._linux += entry.getLinuxCount()
        
    def _buildResult(self) -> EntryOSCount:
        return EntryOSCount(self._windows, self._mac, self._linux)