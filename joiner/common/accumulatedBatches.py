from entryParsing.common.headerInterface import HeaderInterface
from entryParsing.common.table import Table

class AccumulatedBatches:
    def __init__(self, clientId):
        self._pendingTags = []
        self._gamesBatches = bytes()
        self._reviewsBatches = bytes()
        self._clientId = clientId

    def accumulatedLen(self):
        return len(self._pendingTags)

    def toAck(self):
        return self._pendingTags
    
    """
    returns true if could accumulate (same client same table),
    false if it should already process this entries and begin a new
    accumulator
    """
    def accumulate(self, tag, header: HeaderInterface, batch) -> bool:
        if header.getClient() != self._clientId:
            return False
        
        self._pendingTags.append(tag)
        match header.getTable():
            case Table.GAMES:
                self._gamesBatches += batch
            case Table.REVIEWS:
                self._reviewsBatches += batch
        return True
    
    def __str__(self):
        return f"tags: {self._pendingTags} client: {self._clientId}"

    def getGamesBatches(self):
        return self._gamesBatches
    
    def getReviewsBatches(self):
        return self._reviewsBatches
    
    def getClient(self):
        return self._clientId