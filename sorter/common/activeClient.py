import csv
import os
from entryParsing.common.header import Header
from entryParsing.entry import EntryInterface
from packetTracker.packetTracker import PacketTracker

class ActiveClient:
    def __init__(self, tracker: PacketTracker, clientId: str, entryType: type):
        self._clientId = clientId
        self._entryType = entryType
        self._tracker = tracker
        self._partialTop = []
        self._folderPath = f"/{os.getenv('LISTENING_QUEUE')}/clientData/"
        os.makedirs(self._folderPath, exist_ok=True)

    def isDone(self):
        return self._tracker.isDone()
    
    def update(self, header: Header):
        self._tracker.update(header)
    
    def isDuplicate(self, header: Header) -> bool:
        return self._tracker.isDuplicate(header)

    def storeEntry(self, entry: EntryInterface):
        filepath = self._folderPath + f'{self._clientId}.tmp'
        with open(filepath, 'a+') as file:
            file.write(entry.csv())

    def loadEntries(self):
        filepath = self._folderPath + f'{self._clientId}.csv'
        with open(filepath, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                yield self._entryType.fromArgs(row)


    