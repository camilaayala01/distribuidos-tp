import unittest
from datetime import datetime

from ..dateFilterer.dateFilterer import DateFilterer
from ..dateFilterer.dateFilterer import EntryDateFilterer

class TestDateFilterer(unittest.TestCase):
    def setUp(self):
        self.allDecade = [
            EntryDateFilterer("Fallout", datetime.strptime("2015-01-01", "%Y-%m-%d"), 123456),
            EntryDateFilterer("Mirrors Edge", datetime.strptime("2019-12-31", "%Y-%m-%d"), 123),
            EntryDateFilterer("Final Fantasy XV", datetime.strptime("2010-01-01", "%Y-%m-%d"), 123412156),
        ]

        self.noneDecade = [
            EntryDateFilterer("Doki Doki Literature Club", datetime.strptime("2001-02-02", "%Y-%m-%d"), 1),
            EntryDateFilterer("Danganronpa", datetime.strptime("2020-01-01", "%Y-%m-%d"), 1),
        ]

        self.oneDecade = [
            EntryDateFilterer("Final Fantasy XV", datetime.strptime("2010-01-01", "%Y-%m-%d"), 123412156),
            EntryDateFilterer("Doki Doki Literature Club", datetime.strptime("2001-02-02", "%Y-%m-%d"), 1),
            EntryDateFilterer("Danganronpa", datetime.strptime("2020-01-01", "%Y-%m-%d"), 1),
        ]
        
        self.filterer = DateFilterer(datetime.strptime("2010-01-01", "%Y-%m-%d"), datetime.strptime("2019-12-31", "%Y-%m-%d"))

    def testAllDecade(self):
        result = self.filterer.filterBatch(self.allDecade)
        ids = [entry._name for entry in result]
        expectedIds = ["Fallout", "Mirrors Edge", "Final Fantasy XV"]

        self.assertEqual(len(result), len(self.allDecade))
        self.assertEqual(ids, expectedIds)

    def testNoneDecade(self):
        result = self.filterer.filterBatch(self.noneDecade)
        self.assertEqual(len(result), 0)

    def testOneDecade(self):
        result = self.filterer.filterBatch(self.oneDecade)
        ids = [entry._name for entry in result]
        expectedIds = ["Final Fantasy XV"]
        self.assertEqual(len(result), 1)
        self.assertEqual(ids, expectedIds)

 
if __name__ == '__main__':
    unittest.main()
