from entryParsing.common.header import Header
from packetTracker.tracker import TrackerInterface

class PacketTracker(TrackerInterface):
    def __init__(self, nodesInCluster: int, module: int):
        self._nodesInCluster = nodesInCluster
        self._module = module
        self._biggestFragment = 0
        self._pending = set()
        self._receivedEnd = False
    
    @classmethod
    #[biggestFragment,pending,receivedEnd]
    def fromStorage(cls, nodesInCluster: int, module: int, row: list[str]):
        tracker = cls(nodesInCluster, module)
        tracker._biggestFragment = int(row[0])
        tracker._pending = eval(row[1])
        tracker._receivedEnd = bool(row[2])
        return tracker

    def isDuplicate(self, header: Header):
        newFrag = header.getFragmentNumber()
        return newFrag <= self._biggestFragment and newFrag not in self._pending

    def update(self, header: Header):
        newFrag = header.getFragmentNumber()

        if newFrag > self._biggestFragment:
            for num in range (self._biggestFragment + 1, newFrag):
                if num % self._nodesInCluster == self._module:
                    self._pending.add(num) 

            self._biggestFragment = newFrag
            self._receivedEnd = header.isEOF()
        else:
            self._pending.discard(newFrag)

    def isDone(self):
        return len(self._pending) == 0 and self._receivedEnd
        
    def __repr__(self):
        return f"Max: {self._biggestFragment}, Pending: {self._pending}, Eof: {self._receivedEnd}"
    
    def reset(self):
        self._biggestFragment = 0
        self._pending = set()
        self._receivedEnd = False
    
    def asCSVRow(self):
        return self.__dict__.values()
    
