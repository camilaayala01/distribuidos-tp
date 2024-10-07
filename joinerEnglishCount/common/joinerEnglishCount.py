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

class JoinerNegativeReviewsEnglishCount:
    def __init__(self, id: str):
        id = os.getenv('NODE_ID')
        self._internalCommunication = InternalCommunication(name=os.getenv('JOIN_ENG_COUNT_MORE_REV'), nodeID=id)
        self._id = int(id)
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
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def _handleEntries(self, entries: list[EntryAppIDNameReviewCount])-> list[str]:
        ready = []
        for entry in entries:
            id = entry.getAppID()

            if id in self._sent:
                continue

            priorEntry = self._counts.get(id, EntryNameReviewCount(entry.getName(), 0))
            if priorEntry.getCount() + entry.getCount() >= REQUIRED_REVIEWS:
                ready.append(EntryName(priorEntry.getName()))
                self._sent.add(id)
                self._counts.pop(id, None)
            else:
                self._counts[id] = priorEntry.addToCount(entry.getCount())

        return ready

    # should have a fragment number to stream results to client
    def handleMessage(self, ch, method, properties, body):
        header, data = Header.deserialize(body)
        if self._packetTracker.isDuplicate(header):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
        entries = EntryAppIDNameReviewCount.deserialize(data)
        ready = self._handleEntries(entries)
        self._handleSending(ready)
        ch.basic_ack(delivery_tag = method.delivery_tag)
        
    def _sendToNextStep(self, data: bytes):
        self._internalCommunication.sendToDispatcher(data)

    def _handleSending(self, ready: list[EntryName]):
        namesBytes = EntryName.serializeAll(ready)        
        headerBytes = HeaderWithQueryNumber(self._fragnum, self._packetTracker.isDone(), 4).serialize()
        self._sendToNextStep(headerBytes + namesBytes)

        if self._packetTracker.isDone():
            self.reset()