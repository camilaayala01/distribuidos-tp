import os
import unittest
from unittest.mock import MagicMock, patch
from entryParsing.entryAppID import EntryAppID
from grouper.common.grouper import Grouper

class TestGrouperAppIDName(unittest.TestCase):
    @patch('internalCommunication.internalCommunication.InternalCommunication.__init__', MagicMock(return_value=None))
    def setUp(self):
        self._entries = [
            EntryAppID('1'),
            EntryAppID('2'),
            EntryAppID('3'),
            EntryAppID('4'),
            EntryAppID('1'),
            EntryAppID('2'),
            EntryAppID('3'),
            EntryAppID('1'),
            EntryAppID('2'),
            EntryAppID('1'),
        ]
        os.environ['ENTRY_PATH']='entryParsing'
        os.environ['ENTRY_TYPE'] = 'EntryAppID'
        os.environ['GROUPER_TYPE'] = '1'
        os.environ['LISTENING_QUEUE'] = 'Grouper'
        os.environ['NEXT_NODES'] = 'Joiner'
        self._grouper = Grouper()

    def testCountEntries(self):
        result = self._grouper._grouperType.getResults(self._entries)
        hash_dict = {entry._appID: entry for entry in result}
        self.assertEqual(hash_dict["1"].getCount(), 4)
        self.assertEqual(hash_dict["2"].getCount(), 3)
        self.assertEqual(hash_dict["3"].getCount(), 2)
        self.assertEqual(hash_dict["4"].getCount(), 1)
        self.assertEqual(hash_dict.get("5"), None)

if __name__ == '__main__':
    unittest.main()