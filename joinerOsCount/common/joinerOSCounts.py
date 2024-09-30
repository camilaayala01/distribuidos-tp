import os
from entryParsing.common.header import Header
from entryParsing.entryOSCount import EntryOSCount
from internalCommunication.internalComunication import InternalCommunication

class JoinerOSCount:
    def __init__(self):
        self._internalComunnication = InternalCommunication(os.getenv('JOIN_OS'), os.getenv('NODE_ID'))
        self._windows = 0
        self._mac = 0
        self._linux = 0

    def _processMessage(self, data: bytes):
        header, rest = Header.deserialize(data)
        osCount = EntryOSCount.deserialize(rest)
        self._sum(osCount)
        # add extra logic to see if it was the last step or not, or if it was the last fragment
        # but still need to get some that got missing in the middle

    def _sum(self, entry: EntryOSCount):
        self._windows += entry.getWindowsCount()
        self._mac += entry.getMacCount()
        self._linux += entry.getLinuxCount()
        
    def _buildResult(self) -> EntryOSCount:
        return EntryOSCount(self._windows, self._mac, self._linux)