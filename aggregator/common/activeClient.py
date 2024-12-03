import os
import csv
from uuid import UUID
from packetTracker.tracker import TrackerInterface
from statefulNode.activeClient import ActiveClient

class AggregatorClient(ActiveClient):
    def __init__(self, clientId: UUID, tracker: TrackerInterface):
        super().__init__(clientId, fragment=1, tracker=tracker)

    # sendingFragments is true if it will be sending data this time
    def storeFragment(self, storageFile, sendingFragments: bool):
        writer = csv.writer(storageFile, quoting=csv.QUOTE_MINIMAL)
        # stores the fragment it will use next time it needs to send data
        writer.writerow([self._fragment + (1 if sendingFragments else 0)])

    def loadFragment(self, filepath):
        self.loadFragmentFromPath(filepath)

    def loadEntries(self, entryType):
        return super().loadEntries(entryType, self.storagePath() + '.csv')