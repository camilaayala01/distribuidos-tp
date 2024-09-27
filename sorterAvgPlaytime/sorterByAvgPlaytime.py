from entryNameAvgPlaytime import EntryNameAvgPlaytime

TOP_AMOUNT = 10

class SorterByAvgPlaytime:
    def __init__(self, topAmount: int = TOP_AMOUNT): # for testing purposes
        self._type = "SorterPlaytime"
        self._topAmount = topAmount
        self._partialTop = None

    def execute(self, data: bytes):
        # communication is not developed
        print("work in progress")

    def getBatchTop(self, batch: list[EntryNameAvgPlaytime]) -> list[EntryNameAvgPlaytime]:
        sortedBatch = EntryNameAvgPlaytime.sort(batch)
        return sortedBatch[:self._topAmount]

    def mergeKeepTop(self, batch: list[EntryNameAvgPlaytime]):
        newBatchTop = self.getBatchTop(batch)

        if len(newBatchTop) == 0:
            return
        
        if self._partialTop is None:
            self._partialTop = newBatchTop[:self._topAmount]
            return

        i, j = 0, 0
        mergedList = []

        while i < len(self._partialTop) and j < len(newBatchTop):
            if self._partialTop[i].isGreaterThan(newBatchTop[j]):
                mergedList.append(self._partialTop[i])
                i += 1
            else:
                mergedList.append(newBatchTop[j])
                j += 1

        if len(mergedList) < self._topAmount:
            mergedList.extend(self._partialTop[i:])
            mergedList.extend(newBatchTop[j:])
        # no else: since i have all top elements needed, theres no need to entend merged list with the remainings
        
        self._partialTop = mergedList[:self._topAmount]