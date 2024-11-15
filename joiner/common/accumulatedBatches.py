from entryParsing.common.headerInterface import HeaderInterface


class AccumulatedBatches:
    def __init__(self, tag, table, clientId, batch):
        self._pendingTags = [tag]
        self._table = table
        self._batches = [batch]
        self._clientId = clientId

    def accumulatedLen(self):
        return len(self._pendingTags)
    
    """
    returns true if could accumulate (same client same table),
    false if it should already process this entries and begin a new
    accumulator
    """
    def accumulate(self, header: HeaderInterface, tag, batch) -> bool:
        if header.getClient() != self._clientId or header.getTable() != self._table:
            return False
        self._batches.extend(batch)
        self._pendingTags.append(tag)
        return True
    
    def getBatches(self):
        return self._batches
    
    def getTable(self):
        return self._table