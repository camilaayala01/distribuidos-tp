import os
import unittest
from unittest.mock import MagicMock, patch
from entryParsing.entryOSCount import EntryOSCount
from entryParsing.entryOSSupport import EntryOSSupport
from grouper.common.grouper import Grouper

class TestGrouperOSCount(unittest.TestCase):
    @patch('internalCommunication.internalCommunication.InternalCommunication.__init__', MagicMock(return_value=None))
    def setUp(self):
        self._entries = [
            EntryOSSupport(True, True, False),
            EntryOSSupport(True, False, False),
            EntryOSSupport(False, False, False),
            EntryOSSupport(False, True, True),
            EntryOSSupport(False, True, False),
            EntryOSSupport(True, True, False)
        ]
        os.environ['ENTRY_PATH']='entryParsing'
        os.environ['ENTRY_TYPE'] = 'EntryOSSupport'
        os.environ['GROUPER_TYPE'] = '0'
        os.environ['LISTENING_QUEUE'] = 'Grouper'
        os.environ['NEXT_NODES'] = 'Joiner'
        os.environ['HEADER_PATH']='entryParsing.common'
        os.environ['HEADER_TYPE']='Header'
        self._grouper = Grouper()

    def testCountEntries(self):
        result = self._grouper._grouperType.getResults(self._entries)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]._windows, 3)
        self.assertEqual(result[0]._mac, 4)
        self.assertEqual(result[0]._linux, 1)
        self.assertEqual(result[0]._total, 6)

if __name__ == '__main__':
    unittest.main()