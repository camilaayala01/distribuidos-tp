import unittest
from datetime import datetime

from ..indieFilterer.indieFilterer import IndieFilterer
from ..indieFilterer.indieFilterer import EntryIndieFilterer

class TestEnglishFilterer(unittest.TestCase):
    def setUp(self):
        self.allIndie = [
            EntryIndieFilterer("12345", "Fallout", "Indie,Shooter", datetime.strptime("2015-01-01", "%Y-%m-%d"), 12),
            EntryIndieFilterer("12346", "Mirrors Edge", "Indie", datetime.strptime("2015-01-01", "%Y-%m-%d"), 12),
            EntryIndieFilterer("12347", "Final Fantasy XV", "Indie", datetime.strptime("2015-01-01", "%Y-%m-%d"), 12),
        ]

        self.noneIndie = [
            EntryIndieFilterer("123", "Doki Doki Literature Club", "Visual novel", datetime.strptime("2015-01-01", "%Y-%m-%d"), 12),
            EntryIndieFilterer("124", "Danganronpa", "Visual novel", datetime.strptime("2015-01-01", "%Y-%m-%d"), 12),
        ]

        self.oneIndie = [
            EntryIndieFilterer("12345", "Fallout", "Indie,Shooter", datetime.strptime("2015-01-01", "%Y-%m-%d"), 12),
            EntryIndieFilterer("123", "Doki Doki Literature Club", "Visual novel", datetime.strptime("2015-01-01", "%Y-%m-%d"), 12),
            EntryIndieFilterer("124", "Danganronpa", "Visual novel", datetime.strptime("2015-01-01", "%Y-%m-%d"), 12),
        ]
        
        self.filterer = IndieFilterer()

    def testAllIndie(self):
        result = self.filterer.filterBatch(self.allIndie)
        ids = [entry._name for entry in result]
        expectedIds = ["Fallout", "Mirrors Edge", "Final Fantasy XV"]
        self.assertEqual(len(result), len(self.allIndie))
        self.assertEqual(ids, expectedIds)

    def testNoneIndie(self):
        result = self.filterer.filterBatch(self.noneIndie)
        self.assertEqual(len(result), 0)

    def testOneIndie(self):
        result = self.filterer.filterBatch(self.oneIndie)
        ids = [entry._name for entry in result]
        expectedIds = ["Fallout"]
        self.assertEqual(len(result), 1)
        self.assertEqual(ids, expectedIds)

 
if __name__ == '__main__':
    unittest.main()
