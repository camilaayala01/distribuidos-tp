import os
from entryParsing.entryOSCount import EntryOSCount
from entryParsing.entryOSSupport import EntryOSSupport
from entryParsing.common.header import Header
from entryParsing.common.utils import getShardingKey
from internalCommunication.internalCommunication import InternalCommunication

class GrouperOSCounts:
    def __init__(self): 
        self._internalComunnication = InternalCommunication(os.getenv('GROUP_OS'), os.getenv('NODE_ID'))

    def handleMessage(self, ch, method, properties, body):
        header, data = Header.deserialize(body)
        entries = EntryOSSupport.deserialize(data)
        result = self._applyStep(entries)
        msg = header.serialize() + result.serialize()
        self._internalComunnication.sendToOSCountsJoiner(getShardingKey(header._fragment, os.getenv('JOIN_OS_COUNT')), msg)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def _applyStep(self, entries: list['EntryOSSupport']) -> EntryOSCount:
        return self._buildResult(self._count(entries))
    
    def _count(self, entries: list['EntryOSSupport']) -> list[int, int, int]:
        windowsCount, macCount, linuxCount = 0, 0, 0 
        for entry in entries:
            if entry._windows:
                windowsCount += 1
            if entry._mac:
                macCount +=1
            if entry._linux:
                linuxCount +=1
            return [windowsCount, macCount, linuxCount]
        
    def _buildResult(self, counts: list[int]) -> EntryOSCount:
        return EntryOSCount(counts[0], counts[1], counts[2])
    
    def execute(self):
        self._internalComunnication.defineMessageHandler(self.handleMessage)
    
        

        