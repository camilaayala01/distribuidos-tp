import unittest
from unittest.mock import MagicMock, patch
from entryParsing.entryOSCount import EntryOSCount
from common.joinerOSCount import JoinerOSCount

class TestJoinerOSCount(unittest.TestCase):
    @patch('internalCommunication.internalCommunication.InternalCommunication.__init__', MagicMock(return_value=None))
    def setUp(self):
        self._entries = [
            EntryOSCount(1, 2, 3, 5),
            EntryOSCount(1, 2, 3, 5),
            EntryOSCount(1, 2, 3, 5),
            EntryOSCount(1, 2, 3, 5),
        ]
        self._joiner = JoinerOSCount()

    def testCountEntries(self):
        for entry in self._entries:
            self._joiner._sum(entry)
        result = self._joiner._buildResult()
        self.assertEqual(result._windows, 4)
        self.assertEqual(result._mac, 8)
        self.assertEqual(result._linux, 12)
        self.assertEqual(result._total, 20)

if __name__ == '__main__':
    unittest.main()
