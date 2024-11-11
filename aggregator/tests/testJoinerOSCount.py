import unittest
import os
from unittest.mock import MagicMock, patch
import uuid
from entryParsing.entryOSCount import EntryOSCount
from packetTracker.defaultTracker import DefaultTracker
from ..common.aggregator import Aggregator
from ..common.activeClient import ActiveClient

class TestJoinerOSCount(unittest.TestCase):
    @patch('internalCommunication.internalCommunication.InternalCommunication.__init__', MagicMock(return_value=None))
    @patch('os.makedirs', MagicMock(return_value=None))
    def setUp(self):
        self._clientId = uuid.UUID('6bbe9f2a-1c58-4951-a92c-3f2b05147a29').bytes
        self._entries = [
            EntryOSCount(1, 2, 3, 5),
            EntryOSCount(1, 2, 3, 5),
            EntryOSCount(1, 2, 3, 5),
            EntryOSCount(1, 2, 3, 5),
        ]
        os.environ['AGGREGATOR_TYPE'] = '0'
        os.environ['LISTENING_QUEUE'] = 'JoinerOsCounts'
        os.environ['NEXT_NODES'] = 'Some'
        os.environ['ENTRY_PATH']='entryParsing'
        os.environ['ENTRY_TYPE']='EntryOSSupport'
        os.environ['HEADER_PATH']='entryParsing.common'
        os.environ['HEADER_TYPE']='Header'
        self.joiner = Aggregator()
        self.joiner._currentClient = ActiveClient(self.joiner._aggregatorType.getInitialResults(), DefaultTracker("test"))

    def testCountEntries(self):
        results = self.joiner._currentClient._partialRes
        for entry in self._entries:
            _, results, _ = self.joiner._aggregatorType.getOSCountResults(results, entry, False)
        self.assertEqual(results._windows, 4)
        self.assertEqual(results._mac, 8)
        self.assertEqual(results._linux, 12)
        self.assertEqual(results._total, 20)

if __name__ == '__main__':
    unittest.main()