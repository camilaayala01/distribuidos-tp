import os
import unittest
from unittest.mock import MagicMock, patch
import uuid
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from sorter.common.sorter import Sorter

SMALL_TEST_TOP_AMOUNT = 3

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
        
        # action consolidator
        os.environ['ENTRY_TYPE']='EntryAppIDNameReviewCount'
        os.environ['SORTER_TYPE'] = '4'
        os.environ['TOP_AMOUNT'] = '100000000000000'
        self.sorterAction = Sorter()
        self.sorterAction._topAmount=None

    def testGetBatchTopInAscendingOrder(self):
        result = self.sorterAction.getBatchTop(self.entriesMore)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game H", "Game I", "Game G", "Game F"]


        self.assertEqual(len(result), len(self.entriesMore))
        self.assertEqual(topNames, expectedNames)

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


if __name__ == '__main__':
    unittest.main()
