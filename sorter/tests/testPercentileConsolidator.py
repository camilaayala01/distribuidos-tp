import os
import unittest
from unittest.mock import MagicMock, patch

from sorterConsolidatorActionPercentile.common.sorterConsolidatorActionPercentile import SorterConsolidatorActionPercentile

class TestSorterGeneral(unittest.TestCase):
    @patch('internalCommunication.internalCommunication.InternalCommunication.__init__', MagicMock(return_value=None))
    def setUp(self):
        os.environ['NODE_ID'] = '1'
        os.environ['CONS_SORT_PERC_NEG_REV'] = "consolidator"
        os.environ['JOIN_PERC_NEG_REV_COUNT'] = '2'
        self.consolidator = SorterConsolidatorActionPercentile()

    def testUniqueValues(self):
        self.consolidator._partialTop = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.consolidator._filterByPercentile()
        self.assertEqual(self.consolidator._partialTop, [10])

    def testSomeRepeatedValues(self):
        self.consolidator._partialTop = [1, 2, 2, 2, 3, 3, 4, 5, 5, 5]
        self.consolidator._filterByPercentile()
        self.assertEqual(self.consolidator._partialTop, [5, 5, 5])

    def testSomeRepeatedValues(self):
        self.consolidator._partialTop = [1, 2, 2, 2, 3, 3, 4, 5, 5, 5]
        self.consolidator._filterByPercentile()
        self.assertEqual(self.consolidator._partialTop, [5, 5, 5])

    def testAllSameValues(self):
        data = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
        self.consolidator._partialTop = data
        self.consolidator._filterByPercentile()
        self.assertEqual(self.consolidator._partialTop, data)

    def testSmallList(self):
        self.consolidator._partialTop = [1, 2, 3]
        self.consolidator._filterByPercentile()
        self.assertEqual(self.consolidator._partialTop, [3])

    def testEmptyList(self):
        self.consolidator._partialTop = []
        self.consolidator._filterByPercentile()
        self.assertEqual(self.consolidator._partialTop, [])



if __name__ == '__main__':
    unittest.main()
