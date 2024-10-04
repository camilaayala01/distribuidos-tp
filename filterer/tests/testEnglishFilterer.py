import unittest
from datetime import datetime

from ..englishFilterer.englishFilterer import EntryEnglishFilterer
from ..englishFilterer.englishFilterer import EnglishFilterer

class TestEnglishFilterer(unittest.TestCase):
    def setUp(self):
        self.allEnglish = [
            EntryEnglishFilterer("12345", "Fallout", "This game is really good"),
            EntryEnglishFilterer("12346", "Mirrors Edge", "This game ruined my life"),
            EntryEnglishFilterer("12347", "Final Fantasy XV", "Unfollow me now this is the only thing I'll talk about"),
        ]

        self.noneEnglish = [
            EntryEnglishFilterer("123", "Doki Doki Literature Club", "Que buen juego loco"),
            EntryEnglishFilterer("124", "Danganronpa", "Me gustan las monas chinas"),
        ]

        self.oneEnglish = [
            EntryEnglishFilterer("12345", "Fallout", "This game is really good"),
            EntryEnglishFilterer("123", "Doki Doki Literature Club", "Que buen juego loco"),
            EntryEnglishFilterer("124", "Danganronpa", "Me gustan las monas chinas"),
        ]
        
        self.filterer = EnglishFilterer('en')

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
