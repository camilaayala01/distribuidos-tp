import os
import unittest
from unittest.mock import MagicMock, patch

from entryParsing.entryAppID import EntryAppID
from grouperActionEnglish.common.grouperActionEnglish import GrouperActionEnglishNegativeReviews


class TestGrouperPositiveReviews(unittest.TestCase):
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
        os.environ['NODE_ID'] = '1'
        os.environ['GROUP_ENG_NEG_REV'] = 'grouper'
        self._grouper = GrouperActionEnglishNegativeReviews()

    def testCountEntries(self):
        result = self._grouper._count(self._entries)
        self.assertEqual(result[self._entries[0]._appID], 4)
        self.assertEqual(result[self._entries[1]._appID], 3)
        self.assertEqual(result[self._entries[2]._appID], 2)
        self.assertEqual(result[self._entries[3]._appID], 1)
        self.assertEqual(result.get(5), None)

if __name__ == '__main__':
    unittest.main()
