import os
import random
import unittest
from unittest.mock import MagicMock, patch

from entryParsing.common.headerWithSender import HeaderWithSender
from sorterConsolidatorActionPercentile.common.sorterConsolidatorActionPercentile import SorterConsolidatorActionPercentile
from sorterIndiePositiveReviews.common.sorterIndiePositiveReviews import SorterIndiePositiveReviews
from entryParsing.entryNameReviewCount import EntryNameReviewCount

SMALL_TEST_TOP_AMOUNT = 3
BIG_TEST_TOP_AMOUNT = 20

# sorter by average playtime is not included, since it acts the same way as sorter by positive reviews
class TestSorterGeneral(unittest.TestCase):
    @patch('internalCommunication.internalCommunication.InternalCommunication.__init__', MagicMock(return_value=None))
    def setUp(self):
        self.entriesEqual = [
            EntryNameReviewCount("Game A", 100),
            EntryNameReviewCount("Game B", 120),
            EntryNameReviewCount("Game C", 1100),
        ]

        self.entriesLess = [
            EntryNameReviewCount("Game D", 50),
            EntryNameReviewCount("Game E", 70),
        ]

        self.entriesMore = [
            EntryNameReviewCount("Game F", 150),
            EntryNameReviewCount("Game G", 200),
            EntryNameReviewCount("Game H", 300),
            EntryNameReviewCount("Game I", 250),
        ]
        os.environ['NODE_ID'] = '1'
        os.environ['CONS_SORT_PERC_NEG_REV'] = 'sorterAction'
        os.environ['SORT_INDIE_POS_REV'] = 'sorterIndie'
        os.environ['JOIN_PERC_NEG_REV_COUNT'] = '2'
        os.environ['SORT_INDIE_POS_REV_COUNT'] = '2'

        self.sorterIndieFew = SorterIndiePositiveReviews(SMALL_TEST_TOP_AMOUNT)
        self.sorterAction = SorterConsolidatorActionPercentile()
        self.sorterBig = SorterIndiePositiveReviews(BIG_TEST_TOP_AMOUNT)

    def generateEntries(self):
        entries = []
        for i in range(500):
            entries.append(EntryNameReviewCount(f"Game {i}", random.randint(1, 1000)))

        return entries

    def testGetBatchTopInAscendingOrder(self):
        result = self.sorterAction.getBatchTop(self.entriesMore)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game F", "Game G", "Game I", "Game H"]

        self.assertEqual(len(result), len(self.entriesMore))
        self.assertEqual(topNames, expectedNames)

    def testGetBatchTopWithNoLimit(self):
        entries1 = self.generateEntries()
        entries2 = self.generateEntries()
        self.sorterAction.mergeKeepTop(entries1)
        self.sorterAction.mergeKeepTop(entries2)

        for i in range(len(self.sorterAction._partialTop) - 1):
            self.assertFalse(self.sorterAction._partialTop[i].isGreaterThan(self.sorterAction._partialTop[i + 1]))
        self.assertEqual(len(self.sorterAction._partialTop), len(entries1) + len(entries2))

    def testGetBatchTopWithEqualEntriesToTop(self):
        result = self.sorterIndieFew.getBatchTop(self.entriesEqual)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game C", "Game B", "Game A"]

        self.assertEqual(len(result), len(self.entriesEqual))
        self.assertEqual(topNames, expectedNames)

    def testGetBatchTopWithLessEntriesThanTop(self):
        result = self.sorterIndieFew.getBatchTop(self.entriesLess)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game E", "Game D"]

        self.assertEqual(len(result), len(self.entriesLess))
        self.assertEqual(topNames, expectedNames)

    def testGetBatchTopMoreThanTop(self):
        result = self.sorterIndieFew.getBatchTop(self.entriesMore)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game H", "Game I", "Game G"]

        self.assertEqual(len(result), SMALL_TEST_TOP_AMOUNT)
        self.assertEqual(topNames, expectedNames)

    def testMergeKeepsTop(self):
        self.sorterIndieFew.mergeKeepTop(self.entriesMore)
        self.sorterIndieFew.mergeKeepTop(self.entriesLess)
        self.sorterIndieFew.mergeKeepTop(self.entriesEqual)

        topNames = [entry._name for entry in self.sorterIndieFew._partialTop]
        expectedNames = ["Game C", "Game H", "Game I"]
        self.assertEqual(len(self.sorterIndieFew._partialTop), SMALL_TEST_TOP_AMOUNT)
        self.assertEqual(topNames, expectedNames)

    def testMergeWithBiggerAmountThanTop(self):
        allEntries = self.entriesEqual + self.entriesLess + self.entriesMore
        ordered = self.sorterBig.getBatchTop(allEntries)

        self.sorterBig.mergeKeepTop(self.entriesMore)
        self.sorterBig.mergeKeepTop(self.entriesLess)
        self.sorterBig.mergeKeepTop(self.entriesEqual)

        self.assertEqual(len(self.sorterBig._partialTop), len(allEntries))
        self.assertEqual(self.sorterBig._partialTop, ordered)


if __name__ == '__main__':
    unittest.main()
