import os
import logging
from entryParsing.common.header import Header
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.entryAppIDNameReviewCount import EntryAppIDNameReviewCount
from entryParsing.entryName import EntryName
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from internalCommunication.internalCommunication import InternalCommunication
from packetTracker.defaultTracker import DefaultTracker
from entryParsing.common.utils import initializeLog

REQUIRED_REVIEWS=5000

"""
Entities that join all partial counts and streams results to clients
More than one entity
Query 4
"""

class JoinerNegativeReviewsEnglishCount:
    def __init__(self):
        initializeLog()
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
                priorEntry.addToCount(entry.getCount())
                self._counts[id] = priorEntry

        return ready

    # should have a fragment number to stream results to client
    def handleMessage(self, ch, method, properties, body):
        print(body)
        header, data = Header.deserialize(body)
        print(data)
        logging.info(f'action: received batch | {header} | result: success')
        if self._packetTracker.isDuplicate(header):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
        self._packetTracker.update(header)
        entries = EntryAppIDNameReviewCount.deserialize(data)
        ready = self._handleEntries(entries)
        self._handleSending(ready)
        ch.basic_ack(delivery_tag = method.delivery_tag)
        
    def _sendToNextStep(self, data: bytes):
        self._internalCommunication.sendToStreamJoinerConsolidator(data)

    def _handleSending(self, ready: list[EntryName]):
        header = HeaderWithSender(self._id, self._fragnum, self._packetTracker.isDone())
        if self._packetTracker.isDone() and len(ready) == 0:
            self._sendToNextStep(header.serialize())
            logging.info(f'action: sending to consolidator empty batch | {header} | result: success')
            self.reset()

        if len(ready) == 0:
            return
        
        logging.info(f'action: sending to consolidator batch | {header} | result: success')
        namesBytes = EntryName.serializeAll(ready)        
        self._sendToNextStep(header.serialize() + namesBytes)

        if self._packetTracker.isDone():
            self.reset()