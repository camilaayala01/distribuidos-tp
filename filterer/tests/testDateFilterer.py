import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from entryParsing.entryNameDateAvgPlaytime import EntryNameDateAvgPlaytime
from filtererDate.filtererDate import FiltererDate

class TestDateFilterer(unittest.TestCase):
    @patch('internalCommunication.internalCommunication.InternalCommunication.__init__', MagicMock(return_value=None))
    def setUp(self):
        self.allDecade = [
            EntryNameDateAvgPlaytime("Fallout", "2015-01-01", 123456),
            EntryNameDateAvgPlaytime("Mirrors Edge", "2019-12-31", 123),
            EntryNameDateAvgPlaytime("Final Fantasy XV", "2010-01-01", 123412156),
        ]

        self.noneDecade = [
            EntryNameDateAvgPlaytime("Doki Doki Literature Club","2001-02-02", 1),
            EntryNameDateAvgPlaytime("Danganronpa", "2020-01-01", 1),
        ]

        self.oneDecade = [
            EntryNameDateAvgPlaytime("Final Fantasy XV", "2010-01-01", 123412156),
            EntryNameDateAvgPlaytime("Doki Doki Literature Club", "2001-02-02", 1),
            EntryNameDateAvgPlaytime("Danganronpa", "2020-01-01", 1),
        ]
        
        self.filterer = FiltererDate()

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
