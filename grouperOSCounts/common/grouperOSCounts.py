import os
from entryParsing.common.entryOSParcialCount import EntryOSParcialCount
from entryParsing.common.entryOSSupport import EntryOSSupport
from entryParsing.common.header import Header
from entryParsing.common.utils import getRandomShardingKey, getShardingKey
from internalCommunication.internalComunication import InternalCommunication
class GrouperOSCounts:
    def __init__(self): 
        self._type = os.getenv('GROUP_OS')
        self._internalComunnication = InternalCommunication(self._type)

    def handleMessage(self, ch, method, properties, body):
        header, data = Header.deserialize(body)
        entries = EntryOSSupport.deserialize(data)
        result = self._applyStep(entries)
        msg = header.serialize() + result.serialize()
        self._internalComunnication.sendToOSCountsJoiner(getShardingKey(header._fragment, os.getenv('JOIN_OS_COUNT')), msg)

    def _applyStep(self, entries: list['EntryOSSupport']) -> EntryOSParcialCount:
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
        
    def _buildResult(self, counts: list[int]) -> EntryOSParcialCount:
        return EntryOSParcialCount(counts[0], counts[1], counts[2])
    
    def execute(self):
        self._internalComunnication.defineMessageHandler(self.handleMessage)
    
        

        