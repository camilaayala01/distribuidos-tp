import os
import unittest
from unittest.mock import MagicMock, patch
from entryParsing.entryAppIDNameGenres import EntryAppIDNameGenres
from filterer.common.filterer import Filterer

class TestActionFilterer(unittest.TestCase):
    @patch('internalCommunication.internalCommunication.InternalCommunication.__init__', MagicMock(return_value=None))
    def setUp(self):
        self.allAction = [
            EntryAppIDNameGenres("12345", "Fallout", "Action"),
            EntryAppIDNameGenres("12346", "Mirrors Edge", "Action,Suspense"),
            EntryAppIDNameGenres("12347", "Final Fantasy XV", "Action,Fantasy"),
        ]

        self.noneAction = [
            EntryAppIDNameGenres("123", "Doki Doki Literature Club", "Horror,Love"),
            EntryAppIDNameGenres("124", "Danganronpa", "Visual novel"),
        ]

        self.oneAction = [
            EntryAppIDNameGenres("123", "Doki Doki Literature Club", "Horror,Love"),
            EntryAppIDNameGenres("12346", "Mirrors Edge", "Action,Suspense"),
            EntryAppIDNameGenres("124", "Danganronpa", "Visual novel"),
        ]
        
        os.environ['FILTERER_TYPE'] = '2'
        os.environ['LISTENING_QUEUE'] = 'FilterAction'
        os.environ['NEXT_NODES'] = 'JoinerActionNegativeReviewsEnglish,2,0;JoinerActionPercentile,2,0'
        os.environ['ENTRY_TYPE']='EntryAppIDNameGenres'
        os.environ['ENTRY_PATH']='entryParsing'
        os.environ['HEADER_PATH']='entryParsing.common'
        os.environ['HEADER_TYPE']='HeaderWithTable'
        self.filterer = Filterer()

    def testAllAction(self):
        result = self.filterer.filterBatch(self.allAction)
        ids = [entry._appID for entry in result]
        expectedIds = ["12345", "12346", "12347"]

        self.assertEqual(len(result), len(self.allAction))
        self.assertEqual(ids, expectedIds)

    def testNoneAction(self):
        result = self.filterer.filterBatch(self.noneAction)
        self.assertEqual(len(result), 0)

    def testOneAction(self):
        result = self.filterer.filterBatch(self.oneAction)
        ids = [entry._appID for entry in result]
        expectedIds = ["12346"]
        self.assertEqual(len(result), 1)
        self.assertEqual(ids, expectedIds)

 
if __name__ == '__main__':
    unittest.main()
