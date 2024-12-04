from entryParsing.headerInterface import HeaderInterface
from entryParsing.common.table import Table

class AccumulatedBatches:
    def __init__(self, clientId: bytes, table: Table):
        self._pendingTags = []
        self._accumulated = bytes()
        self._table = table
        self._clientId = clientId

    def accumulatedLen(self):
        return len(self._pendingTags)

    def toAck(self):
        return self._pendingTags
    
    """
    returns true if could accumulate (same client),
    false if it should already process this entries and begin a new
    accumulator
    """
    def accumulate(self, tag, header: HeaderInterface, batch) -> bool:
        if header.getClient() != self._clientId or self._table != header.getTable():
            return False
        
        self._pendingTags.append(tag)
        self._accumulated += batch
        return True
    
    def __str__(self):
        return f"tags: {self._pendingTags} client: {self._clientId}"

    def getPendingBatches(self):
        return self._accumulated
    
    def getCorrespondingTable(self):
        return self._table

    def getClient(self):
        return self._clientId