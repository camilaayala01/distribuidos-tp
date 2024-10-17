import os
import random
import unittest
from unittest.mock import MagicMock, patch

from entryParsing.entryNameReviewCount import EntryNameReviewCount
from sorter.common.sorter import Sorter

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
        os.environ['NODE_COUNT'] = '2'
        os.environ['PRIOR_NODE_COUNT'] = '2'
        os.environ['LISTENING_QUEUE'] = 'sorter'
        os.environ['NEXT_NODES'] = 'ConsolidatorSorterIndiePositiveReviews'
        os.environ['SORTER_TYPE'] = '1'
        os.environ['TOP_AMOUNT'] = '3'
        # indie
        self.sorterIndieFew = Sorter()
        os.environ['TOP_AMOUNT'] = '20'
        self.sorterBig = Sorter()
        os.environ['SORTER_TYPE'] = '4'
        # action consolidator
        self.sorterAction = Sorter()
        

    def generateEntries(self):
        entries = []
        for i in range(500):
            entries.append(EntryNameReviewCount(f"Game {i}", random.randint(1, 1000)))

        return entries

    def testGetBatchTopInAscendingOrder(self):
        result = self.sorterAction._sorterType.getBatchTop(self.entriesMore, self.sorterAction._topAmount)
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
        result = self.sorterIndieFew._sorterType.getBatchTop(self.entriesEqual, self.sorterIndieFew._topAmount)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game C", "Game B", "Game A"]

        self.assertEqual(len(result), len(self.entriesEqual))
        self.assertEqual(topNames, expectedNames)

    def testGetBatchTopWithLessEntriesThanTop(self):
        result = self.sorterIndieFew._sorterType.getBatchTop(self.entriesLess, self.sorterIndieFew._topAmount)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game E", "Game D"]

        self.assertEqual(len(result), len(self.entriesLess))
        self.assertEqual(topNames, expectedNames)

    def testGetBatchTopMoreThanTop(self):
        result = self.sorterIndieFew._sorterType.getBatchTop(self.entriesMore,self.sorterIndieFew._topAmount)
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
        ordered = self.sorterBig._sorterType.getBatchTop(allEntries, self.sorterBig._topAmount)

        self.sorterBig.mergeKeepTop(self.entriesMore)
        self.sorterBig.mergeKeepTop(self.entriesLess)
        self.sorterBig.mergeKeepTop(self.entriesEqual)

        self.assertEqual(len(self.sorterBig._partialTop), len(allEntries))
        self.assertEqual(self.sorterBig._partialTop, ordered)


if __name__ == '__main__':
    unittest.main()
