import os
from entryParsing.common.header import Header
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.entryAppIDNameReviewCount import EntryAppIDNameReviewCount
from entryParsing.entryName import EntryName
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from entryParsing.entryOSCount import EntryOSCount
from internalCommunication.internalCommunication import InternalCommunication
from packetTracker.defaultTracker import DefaultTracker

REQUIRED_REVIEWS=5000

"""
Entities that join all partial counts and streams results to clients
More than one entity
Query 4
"""
class JoinerAppIDCount:
    def __init__(self, id: str):
        # its var is not in env file
        self._internalComunnication = InternalCommunication(os.getenv('JOIN_OS'))
        # id should come from env as well
        self._id = id
        self._packetTracker = DefaultTracker()
        self._counts = {}
        self._sent = set()
        self._fragnum = 1

    def reset(self):
        self._packetTracker.reset()
        self._counts = {}
        self._sent = set()
        self._fragnum = 1

    def execute(self):
        self._internalComunnication.defineMessageHandler(self.handleMessage())

    def _handleEntries(self, entries: list[EntryAppIDNameReviewCount])-> list[str]:
        ready = []
        for entry in entries:
            id = entry.getAppID()

            if id in self._sent:
                continue

            priorEntry = self._counts.get(id, EntryNameReviewCount(entry.getName(), 0))
            if priorEntry.getCount() + entry.getCount() >= REQUIRED_REVIEWS:
                ready.append(priorEntry.getName())
                self._sent.add(entry.getAppID())
                del self._counts[entry.getAppID()]
            else:
                self._counts[entry.getAppID()] = priorEntry.addToCount(entry.getCount())

        return ready

    # should have a fragment number to stream results to client
    def handleMessage(self, ch, method, properties, body):
        header, data = Header.deserialize(body)
        if self._packetTracker.isDuplicate(header):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
        entries = EntryAppIDNameReviewCount.deserialize(data)
        ready = self._handleEntries(entries)
        self._handleSending()
        ch.basic_ack(delivery_tag = method.delivery_tag)
        
    def _sendToNextStep(self, data: bytes):
        self._internalComunnication.sendToDispatcher(data)

    def _handleSending(self, ready: list[EntryName]):
        if self._packetTracker.isDone():
            headerBytes = HeaderWithQueryNumber(self._fragnum, True, 4).deserialize()
            self._sendToNextStep(headerBytes)
            self.reset()
            return
        
        # sender id is missing and should be here, or else add another joiner joiner
        headerBytes = HeaderWithQueryNumber(self._fragnum, False, 4).deserialize()
        namesBytes = EntryName.serializeAll(ready)
        self._sendToNextStep(headerBytes + namesBytes)
        