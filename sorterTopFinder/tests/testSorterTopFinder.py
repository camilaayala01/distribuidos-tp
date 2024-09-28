import random
import unittest

from ..sorterByReviews.common.sorterIndiePositiveReviews import SorterIndiePositiveReviews
from ..sorterByReviews.common.sorterShooterNegativeReviews import SorterActionNegativeReviews
from ..sorterByReviews.common.entryNameReviewCount import EntryNameReviewCount

SMALL_TEST_TOP_AMOUNT = 3
BIG_TEST_TOP_AMOUNT = 20

# sorter by average playtime is not included, since it acts the same way as sorter by positive reviews
class TestSorterTopFinder(unittest.TestCase):
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
        
        self.sorterIndieFew = SorterIndiePositiveReviews(SMALL_TEST_TOP_AMOUNT)
        self.sorterShooter = SorterActionNegativeReviews()

    def generate_entries(self):
        entries = []
        for i in range(500):
            entries.append(EntryNameReviewCount(f"Game {i}", random.randint(1, 1000)))

        return entries

    def test_get_batch_top_in_ascending_order(self):
        result = self.sorterShooter.getBatchTop(self.entriesMore)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game F", "Game G", "Game I", "Game H"]

        self.assertEqual(len(result), len(self.entriesMore))
        self.assertEqual(topNames, expectedNames)


    def test_get_batch_top_with_no_limit(self):
        entries1=self.generate_entries()
        entries2=self.generate_entries()
        self.sorterShooter.mergeKeepTop(entries1)
        self.sorterShooter.mergeKeepTop(entries2)

        for i in range(len(self.sorterShooter._partialTop) - 1):
            self.assertFalse(self.sorterShooter._partialTop[i].isGreaterThan(self.sorterShooter._partialTop[i+1]))
        self.assertEqual(len(self.sorterShooter._partialTop), len(entries1) + len(entries2))


    def test_get_batch_top_with_equal_entries_to_top(self):
        result = self.sorterIndieFew.getBatchTop(self.entriesEqual)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game C", "Game B", "Game A"]

        self.assertEqual(len(result), len(self.entriesEqual))
        self.assertEqual(topNames, expectedNames)

    def test_get_batch_top_with_less_entries_than_top(self):
        result = self.sorterIndieFew.getBatchTop(self.entriesLess)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game E", "Game D"]

        self.assertEqual(len(result), len(self.entriesLess))
        self.assertEqual(topNames, expectedNames)

    def test_get_batch_top_more_than_top(self):
        result = self.sorterIndieFew.getBatchTop(self.entriesMore)
        topNames = [entry._name for entry in result]
        expectedNames = ["Game H", "Game I", "Game G"]

        self.assertEqual(len(result), SMALL_TEST_TOP_AMOUNT)
        self.assertEqual(topNames, expectedNames)

    def test_merge_keeps_top(self):
        self.sorterIndieFew.mergeKeepTop(self.entriesMore)
        self.sorterIndieFew.mergeKeepTop(self.entriesLess)
        self.sorterIndieFew.mergeKeepTop(self.entriesEqual)

        topNames = [entry._name for entry in self.sorterIndieFew._partialTop]
        expectedNames = ["Game C", "Game H", "Game I"]
        self.assertEqual(len(self.sorterIndieFew._partialTop), SMALL_TEST_TOP_AMOUNT)
        self.assertEqual(topNames, expectedNames)

    def test_merge_with_bigger_amount_than_top(self):
        sorterBig = SorterIndiePositiveReviews(BIG_TEST_TOP_AMOUNT)
        allEntries = self.entriesEqual + self.entriesLess + self.entriesMore
        ordered = sorterBig.getBatchTop(allEntries)

        sorterBig.mergeKeepTop(self.entriesMore)
        sorterBig.mergeKeepTop(self.entriesLess)
        sorterBig.mergeKeepTop(self.entriesEqual)

        self.assertEqual(len(sorterBig._partialTop), len(allEntries))
        self.assertEqual(sorterBig._partialTop, ordered)

if __name__ == '__main__':
    unittest.main()
