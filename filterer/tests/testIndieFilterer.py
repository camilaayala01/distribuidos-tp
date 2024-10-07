import unittest
from unittest.mock import MagicMock, patch

from entryParsing.entryAppIDNameGenresReleaseDateAvgPlaytime import EntryAppIDNameGenresReleaseDateAvgPlaytime
from filtererIndie.common.filtererIndie import FiltererIndie


class TestEnglishFilterer(unittest.TestCase):
    @patch('internalCommunication.internalCommunication.InternalCommunication.__init__', MagicMock(return_value=None))
    def setUp(self):
        self.allIndie = [
            EntryAppIDNameGenresReleaseDateAvgPlaytime("12345", "Fallout", "Indie,Shooter", "2015-01-01", 12),
            EntryAppIDNameGenresReleaseDateAvgPlaytime("12346", "Mirrors Edge", "Indie", "2015-01-01", 12),
            EntryAppIDNameGenresReleaseDateAvgPlaytime("12347", "Final Fantasy XV", "Indie", "2015-01-01", 12),
        ]

        self.noneIndie = [
            EntryAppIDNameGenresReleaseDateAvgPlaytime("123", "Doki Doki Literature Club", "Visual novel", "2015-01-01", 12),
            EntryAppIDNameGenresReleaseDateAvgPlaytime("124", "Danganronpa", "Visual novel", "2015-01-01", 12),
        ]

        self.oneIndie = [
            EntryAppIDNameGenresReleaseDateAvgPlaytime("12345", "Fallout", "Indie,Shooter", "2015-01-01", 12),
            EntryAppIDNameGenresReleaseDateAvgPlaytime("123", "Doki Doki Literature Club", "Visual novel", "2015-01-01", 12),
            EntryAppIDNameGenresReleaseDateAvgPlaytime("124", "Danganronpa", "Visual novel", "2015-01-01", 12),
        ]
        
        self.filterer = FiltererIndie()

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
