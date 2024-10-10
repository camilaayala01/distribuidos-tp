import os
import logging
from entryParsing.entryOSCount import EntryOSCount
from entryParsing.entryOSSupport import EntryOSSupport
from entryParsing.common.header import Header
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.utils import initializeLog

"""
Entities that count the amount of reviews in a batch that belong to the same game
grouping them by AppID and sending the a response with AppID, ReviewCount
More than one entity
Query 1
"""

class GrouperOSCounts:
    def __init__(self): 
        initializeLog()
        self._internalCommunication = InternalCommunication(os.getenv('GROUP_OS'), os.getenv('NODE_ID'))

    def stop(self, _signum, _frame):
        self._internalCommunication.stop()

    def handleMessage(self, ch, method, properties, body):
        logging.info(f'action: receiving batch from initializer | result: success')
        header, data = Header.deserialize(body)
        entries = EntryOSSupport.deserialize(data)
        result = self._applyStep(entries)
        logging.info(f'action: grouping batch by supported OS | result: success')
        msg = header.serialize() + result.serialize()
        self._internalCommunication.sendToOSCountsJoiner(msg)
        logging.info(f'action: sending batch to OS counts joiner | result: success')
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def _applyStep(self, entries: list['EntryOSSupport']) -> EntryOSCount:
        return self._buildResult(self._count(entries))
    
    def _count(self, entries: list['EntryOSSupport']) -> list[int, int, int, int]:
        windowsCount, macCount, linuxCount, total = 0, 0, 0, 0 
        for entry in entries:
            total += 1
            if entry._windows:
                windowsCount += 1
            if entry._mac:
                macCount +=1
            if entry._linux:
                linuxCount +=1
        logging.info(f'action: finish count | total: {total} | windows: {windowsCount} | mac: {macCount} | linux: {linuxCount} | result: success')
        return [windowsCount, macCount, linuxCount, total]
        
    def _buildResult(self, counts: list[int]) -> EntryOSCount:
        return EntryOSCount(counts[0], counts[1], counts[2], counts[3])
    
    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)
    
        

        