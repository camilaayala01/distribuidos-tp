import unittest

from sorterIndiePositiveReviews.common.sorterIndiePositiveReviews import SorterByAvgPlaytime
from sorterIndiePositiveReviews.common.entryNameReviewCount import EntryNameReviewCount

SMALL_TEST_TOP_AMOUNT = 3
BIG_TEST_TOP_AMOUNT = 20

class TestSorterByAvgPlaytime(unittest.TestCase):
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
        self.sorterFew = SorterByAvgPlaytime(SMALL_TEST_TOP_AMOUNT)

    def test_get_batch_top_with_equal_entries_to_top(self):
        result = self.sorterFew.getBatchTop(self.entriesEqual)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game C", "Game B", "Game A"]

        self.assertEqual(len(result), len(self.entriesEqual))
        self.assertEqual(topNames, expectedNames)

    def test_get_batch_top_with_less_entries_than_top(self):
        result = self.sorterFew.getBatchTop(self.entriesLess)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game E", "Game D"]

        self.assertEqual(len(result), len(self.entriesLess))
        self.assertEqual(topNames, expectedNames)

    def test_get_batch_top_more_than_top(self):
        result = self.sorterFew.getBatchTop(self.entriesMore)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game H", "Game I", "Game G"]

        self.assertEqual(len(result), SMALL_TEST_TOP_AMOUNT)
        self.assertEqual(topNames, expectedNames)

    def test_merge_keeps_top(self):
        self.sorterFew.mergeKeepTop(self.entriesMore)
        self.sorterFew.mergeKeepTop(self.entriesLess)
        self.sorterFew.mergeKeepTop(self.entriesEqual)

        topNames = [entry._name for entry in self.sorterFew._partialTop]
        expectedNames = ["Game C", "Game H", "Game I"]
        self.assertEqual(len(self.sorterFew._partialTop), SMALL_TEST_TOP_AMOUNT)
        self.assertEqual(topNames, expectedNames)

    def test_merge_with_bigger_amount_than_top(self):
        sorterBig = SorterByAvgPlaytime(BIG_TEST_TOP_AMOUNT)
        allEntries = self.entriesEqual + self.entriesLess + self.entriesMore
        ordered = sorterBig.getBatchTop(allEntries)

        sorterBig.mergeKeepTop(self.entriesMore)
        sorterBig.mergeKeepTop(self.entriesLess)
        sorterBig.mergeKeepTop(self.entriesEqual)

        self.assertEqual(len(sorterBig._partialTop), len(allEntries))
        self.assertEqual(sorterBig._partialTop, ordered)

if __name__ == '__main__':
    unittest.main()
