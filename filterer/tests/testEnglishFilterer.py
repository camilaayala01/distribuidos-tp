import os
import unittest
from unittest.mock import MagicMock, patch

from entryParsing.entryAppIDNameReviewText import EntryAppIDNameReviewText
from filterer.common.filterer import Filterer


class TestEnglishFilterer(unittest.TestCase):
    @patch('internalCommunication.internalCommunication.InternalCommunication.__init__', MagicMock(return_value=None))
    def setUp(self):
        self.allEnglish = [
            EntryAppIDNameReviewText("12345", "Fallout", "This game is really good"),
            EntryAppIDNameReviewText("12346", "Mirrors Edge", "This game ruined my life"),
            EntryAppIDNameReviewText("12347", "Final Fantasy XV", "Unfollow me now this is the only thing I'll talk about"),
        ]

        self.noneEnglish = [
            EntryAppIDNameReviewText("123", "Doki Doki Literature Club", "Que buen juego loco"),
            EntryAppIDNameReviewText("124", "Danganronpa", "Me gustan las monas chinas"),
        ]

        self.oneEnglish = [
            EntryAppIDNameReviewText("12345", "Fallout", "This game is really good"),
            EntryAppIDNameReviewText("123", "Doki Doki Literature Club", "Que buen juego loco"),
            EntryAppIDNameReviewText("124", "Danganronpa", "Me gustan las monas chinas"),
        ]
        
        os.environ['FILTERER_TYPE'] = '3'
        os.environ['LISTENING_QUEUE'] = 'FilterEnglish'
        os.environ['NEXT_NODES'] = 'GrouperActionEnglishNegativeReviews'
        os.environ['ENTRY_TYPE']='EntryAppIDNameReviewText'
        os.environ['ENTRY_PATH']='entryParsing'
        os.environ['HEADER_PATH']='entryParsing.common'
        os.environ['HEADER_TYPE']='HeaderWithSender'
        self.filterer = Filterer()

    def testAllEnglish(self):
        result = self.filterer.filterBatch(self.allEnglish)
        ids = [entry._name for entry in result]
        expectedIds = ["Fallout", "Mirrors Edge", "Final Fantasy XV"]
        self.assertEqual(len(result), len(self.allEnglish))
        self.assertEqual(ids, expectedIds)

    def testNoneEnglish(self):
        result = self.filterer.filterBatch(self.noneEnglish)
        self.assertEqual(len(result), 0)

    def testOneEnglish(self):
        result = self.filterer.filterBatch(self.oneEnglish)
        ids = [entry._name for entry in result]
        expectedIds = ["Fallout"]
        self.assertEqual(len(result), 1)
        self.assertEqual(ids, expectedIds)

 
if __name__ == '__main__':
    unittest.main()
