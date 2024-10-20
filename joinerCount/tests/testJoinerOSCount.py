import unittest
import os
from unittest.mock import MagicMock, patch
from entryParsing.entryOSCount import EntryOSCount
from ..common.joinerCount import JoinerCount

class TestJoinerOSCount(unittest.TestCase):
    @patch('internalCommunication.internalCommunication.InternalCommunication.__init__', MagicMock(return_value=None))
    def setUp(self):
        self._entries = [
            EntryOSCount(1, 2, 3, 5),
            EntryOSCount(1, 2, 3, 5),
            EntryOSCount(1, 2, 3, 5),
            EntryOSCount(1, 2, 3, 5),
        ]
        os.environ['JOINER_COUNT_TYPE'] = '0'
        os.environ['LISTENING_QUEUE'] = 'JoinerOsCounts'
        os.environ['NEXT_NODES'] = 'Some'
        os.environ['ENTRY_PATH']='entryParsing'
        os.environ['ENTRY_TYPE']='EntryOSSupport'
        os.environ['HEADER_PATH']='entryParsing.common'
        os.environ['HEADER_TYPE']='Header'
        self.joiner = JoinerCount()

    def testCountEntries(self):
        results = self.joiner._counts
        for entry in self._entries:
            _, results, _ = self.joiner._joinerCountType.getOSCountResults(results, entry, False)
        self.assertEqual(results._windows, 4)
        self.assertEqual(results._mac, 8)
        self.assertEqual(results._linux, 12)
        self.assertEqual(results._total, 20)

if __name__ == '__main__':
    unittest.main()
