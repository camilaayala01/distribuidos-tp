import os
from entryParsing.common.header import Header
from packetTracker.tracker import TrackerInterface

class PacketTracker(TrackerInterface):
    def __init__(self, nodesInCluster: int, module: int, storagePath: str):
        self._nodesInCluster = nodesInCluster
        self._module = module
        self._biggestFragment = 0 #escribir
        self._pending = set()
        self._receivedEnd = False
        self._storagePath = f"/packetTracker/{storagePath}.txt"
        os.makedirs(f"/packetTracker", exist_ok=True)

    def store(self):
        with open(self._storagePath, 'w+') as file:
            file.write(f"MAX={self._biggestFragment};MISSING={self._pending}")

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
        
        self.store()

    def isDone(self):
        return len(self._pending) == 0 and self._receivedEnd
    
    def reset(self):
        self._biggestFragment = 0
        self._pending = set()
        self._receivedEnd = False