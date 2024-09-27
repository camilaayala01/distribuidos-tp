import unittest

from grouperPositiveReviews.common.entryAppID import EntryAppID
from grouperPositiveReviews.common.grouperPositiveReviews import *


class TestGrouperPositiveReviews(unittest.TestCase):
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
        self._grouper = GrouperPositiveReviews()

    def testCountEntries(self):
        result = self._grouper.count(self._entries)
        self.assertEqual(result[self._entries[0]._appID], 4)
        self.assertEqual(result[self._entries[1]._appID], 3)
        self.assertEqual(result[self._entries[2]._appID], 2)
        self.assertEqual(result[self._entries[3]._appID], 1)
        self.assertEqual(result.get(5), None)

if __name__ == '__main__':
    unittest.main()
