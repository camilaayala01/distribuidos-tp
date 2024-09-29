import os
import random
from entryParsing.common.entryOSParcialCount import EntryOSParcialCount
from entryParsing.common.entryOSSupport import EntryOSSupport
from internalCommunication.internalComunication import InternalCommunication
class GrouperOSCounts:
    def __init__(self): 
        self._type = os.getenv('GROUP_OS')
        self._internalComunnication = InternalCommunication(self._type)

    def handleMessage(self, ch, method, properties, body):
        entries = EntryOSSupport.deserialize(body)
        result = self._applyStep(entries)
        def getShardingKey(nodeCount):
            random.randint(0, nodeCount -1)

        self._internalComunnication.sendToOSCountsJoiner(getShardingKey(os.getenv('JOIN_OS_COUNT')), result.serialize())

    def _applyStep(self, entries: list['EntryOSSupport']) -> EntryOSParcialCount:
        return self._buildResult(self._count(entries))
    
    def _count(self, entries: list['EntryOSSupport']):
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
    
        

        