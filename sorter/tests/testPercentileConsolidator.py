import os
import unittest
from unittest.mock import MagicMock, patch

from entryParsing.entryAppIDNameReviewCount import EntryAppIDNameReviewCount
from sorter.common.sorter import Sorter

class TestSorterGeneral(unittest.TestCase):
    @patch('internalCommunication.internalCommunication.InternalCommunication.__init__', MagicMock(return_value=None))
    def setUp(self):
        os.environ['PRIOR_NODE_COUNT'] = '2'
        os.environ['LISTENING_QUEUE'] = 'sorter'
        os.environ['NEXT_NODES'] = 'nextnode'
        os.environ['SORTER_TYPE'] = '4'
        os.environ['PERCENTILE'] = '90'
        self.consolidator = Sorter()

    def generateEntries(self, reviewCounts):
        entries = []
        for i in reviewCounts:
            entries.append(EntryAppIDNameReviewCount('1','Dota 2', i))
        return entries

    def testUniqueValues(self):
        results = self.consolidator._sorterType.filterByPercentile(self.generateEntries([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
        self.assertEqual(9, results[0].getCount())
        self.assertEqual(10, results[1].getCount())
        self.assertEqual(len(results), 2)

    def testSomeRepeatedValues(self):
        results = self.consolidator._sorterType.filterByPercentile(self.generateEntries([1, 2, 2, 2, 3, 3, 4, 5, 5, 5]))
        self.assertEqual(5, results[0].getCount())
        self.assertEqual(5, results[1].getCount())
        self.assertEqual(5, results[2].getCount())
        self.assertEqual(len(results), 3)

    def testAllSameValues(self):
        data = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
        results = self.consolidator._sorterType.filterByPercentile(self.generateEntries(data))
        self.assertEqual(4, results[0].getCount())
        self.assertEqual(len(results), len(data))

    def testSmallList(self):
        results = self.consolidator._sorterType.filterByPercentile(self.generateEntries([1, 2, 3]))
        self.assertEqual(3, results[0].getCount())
        self.assertEqual(len(results), 1)

    def testEmptyList(self):
        results = self.consolidator._sorterType.filterByPercentile(self.generateEntries([]))
        self.assertEqual([], results)
        self.assertEqual(len(results), 0)



if __name__ == '__main__':
    unittest.main()
