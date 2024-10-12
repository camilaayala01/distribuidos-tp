import os
import unittest
from unittest.mock import MagicMock, patch

from entryParsing.entryAppID import EntryAppID
from entryParsing.entryAppIDName import EntryAppIDName
from grouperActionEnglish.common.grouperActionEnglish import GrouperActionEnglishNegativeReviews


class TestGrouperPositiveReviews(unittest.TestCase):
    @patch('internalCommunication.internalCommunication.InternalCommunication.__init__', MagicMock(return_value=None))
    def setUp(self):
        self._entries = [
            EntryAppIDName('1', 'Rust'),
            EntryAppIDName('2', 'Grand Theft Auto V'),
            EntryAppIDName('3', 'Evolve Stage 2'),
            EntryAppIDName('4', 'theHunter Classic'),
            EntryAppIDName('1', 'Rust'),
            EntryAppIDName('2', 'Grand Theft Auto V'),
            EntryAppIDName('3', 'Evolve Stage 2'),
            EntryAppIDName('1', 'Rust'),
            EntryAppIDName('2', 'Grand Theft Auto V'),
            EntryAppIDName('1', 'Rust'),
        ]
        os.environ['NODE_ID'] = '1'
        os.environ['GROUP_ENG_NEG_REV'] = 'grouper'
        self._grouper = GrouperActionEnglishNegativeReviews()

    def testCountEntries(self):
        result = self._grouper._count(self._entries)
        self.assertEqual(result["1"].getCount(), 4)
        self.assertEqual(result["2"].getCount(), 3)
        self.assertEqual(result["3"].getCount(), 2)
        self.assertEqual(result["4"].getCount(), 1)
        self.assertEqual(result.get("5"), None)

if __name__ == '__main__':
    unittest.main()