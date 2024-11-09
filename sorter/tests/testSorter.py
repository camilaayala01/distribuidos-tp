import os
import random
import unittest
from unittest.mock import MagicMock, patch
import uuid
from sorter.common.activeClient import ActiveClient
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from sorter.common.sorter import Sorter

SMALL_TEST_TOP_AMOUNT = 3
BIG_TEST_TOP_AMOUNT = 20

# sorter by average playtime is not included, since it acts the same way as sorter by positive reviews
class TestSorterGeneral(unittest.TestCase):
    @patch('internalCommunication.internalCommunication.InternalCommunication.__init__', MagicMock(return_value=None))
    @patch('os.makedirs', MagicMock(return_value=None))
    def setUp(self):
        self._clientId = uuid.UUID('6bbe9f2a-1c58-4951-a92c-3f2b05147a29').bytes
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
        os.environ['ENTRY_PATH']='entryParsing'
        os.environ['HEADER_PATH']='entryParsing.common'
        os.environ['HEADER_TYPE']='Header'
        # indie
        os.environ['ENTRY_TYPE']='EntryNameReviewCount'
        self.sorterIndieFew = Sorter()
        os.environ['TOP_AMOUNT'] = '20'
        self.sorterBig = Sorter()
        
        # action consolidator
        os.environ['ENTRY_TYPE']='EntryAppIDNameReviewCount'
        os.environ['SORTER_TYPE'] = '4'
        self.sorterAction = Sorter()
        self.sorterAction._topAmount=None
        

    def generateEntries(self):
        entries = []
        for i in range(500):
            entries.append(EntryNameReviewCount(f"Game {i}", random.randint(1, 1000)))

        return entries

    def testGetBatchTopInAscendingOrder(self):
        result = self.sorterAction._sorterType.getBatchTop(self.entriesMore, self.sorterAction._topAmount, self.sorterAction._entryType)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game F", "Game G", "Game I", "Game H"]

        self.assertEqual(len(result), len(self.entriesMore))
        self.assertEqual(topNames, expectedNames)

    @patch('os.makedirs', MagicMock(return_value=None))
    def testGetBatchTopWithNoLimit(self):
        entries1 = self.generateEntries()
        entries2 = self.generateEntries()
        self.sorterAction._currentClient= ActiveClient(self.sorterAction._sorterType.initializeTracker(self._clientId))
        self.sorterAction.mergeKeepTop(entries1)
        self.sorterAction.mergeKeepTop(entries2)
        for i in range(len(self.sorterAction._currentClient._partialTop) - 1):
            self.assertFalse(self.sorterAction._currentClient._partialTop[i].isGreaterThan(self.sorterAction._currentClient._partialTop[i + 1]))
        self.assertEqual(len(self.sorterAction._currentClient._partialTop), len(entries1) + len(entries2))

    def testGetBatchTopWithEqualEntriesToTop(self):
        result = self.sorterIndieFew._sorterType.getBatchTop(self.entriesEqual, self.sorterIndieFew._topAmount, self.sorterIndieFew._entryType)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game C", "Game B", "Game A"]

        self.assertEqual(len(result), len(self.entriesEqual))
        self.assertEqual(topNames, expectedNames)

    def testGetBatchTopWithLessEntriesThanTop(self):
        result = self.sorterIndieFew._sorterType.getBatchTop(self.entriesLess, self.sorterIndieFew._topAmount, self.sorterIndieFew._entryType)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game E", "Game D"]

        self.assertEqual(len(result), len(self.entriesLess))
        self.assertEqual(topNames, expectedNames)

    def testGetBatchTopMoreThanTop(self):
        result = self.sorterIndieFew._sorterType.getBatchTop(self.entriesMore,self.sorterIndieFew._topAmount, self.sorterIndieFew._entryType)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game H", "Game I", "Game G"]

        self.assertEqual(len(result), SMALL_TEST_TOP_AMOUNT)
        self.assertEqual(topNames, expectedNames)

    @patch('os.makedirs', MagicMock(return_value=None))
    def testMergeKeepsTop(self):
        self.sorterIndieFew._currentClient= ActiveClient(self.sorterIndieFew._sorterType.initializeTracker(self._clientId))
        self.sorterIndieFew.mergeKeepTop(self.entriesMore)
        self.sorterIndieFew.mergeKeepTop(self.entriesLess)
        self.sorterIndieFew.mergeKeepTop(self.entriesEqual)

        topNames = [entry._name for entry in self.sorterIndieFew._currentClient._partialTop]
        expectedNames = ["Game C", "Game H", "Game I"]
        self.assertEqual(len(self.sorterIndieFew._currentClient._partialTop), SMALL_TEST_TOP_AMOUNT)
        self.assertEqual(topNames, expectedNames)

    @patch('os.makedirs', MagicMock(return_value=None))
    def testMergeWithBiggerAmountThanTop(self):
        allEntries = self.entriesEqual + self.entriesLess + self.entriesMore
        ordered = self.sorterBig._sorterType.getBatchTop(allEntries, self.sorterBig._topAmount, self.sorterBig._entryType)
        self.sorterBig._currentClient= ActiveClient(self.sorterBig._sorterType.initializeTracker(self._clientId))
        self.sorterBig.mergeKeepTop(self.entriesMore)
        self.sorterBig.mergeKeepTop(self.entriesLess)
        self.sorterBig.mergeKeepTop(self.entriesEqual)

        self.assertEqual(len(self.sorterBig._currentClient._partialTop), len(allEntries))
        self.assertEqual(self.sorterBig._currentClient._partialTop, ordered)


if __name__ == '__main__':
    unittest.main()
