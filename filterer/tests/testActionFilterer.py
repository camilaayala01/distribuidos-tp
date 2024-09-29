import unittest

from ..actionFilterer.actionFilterer import ActionFilterer
from ..actionFilterer.entryActionFilterer import EntryActionFilterer

class TestActionFilterer(unittest.TestCase):
    def setUp(self):
        self.allAction = [
            EntryActionFilterer("12345", "Fallout", "Action"),
            EntryActionFilterer("12346", "Mirrors Edge", "Action,Suspense"),
            EntryActionFilterer("12347", "Final Fantasy XV", "Action,Fantasy"),
        ]

        self.noneAction = [
            EntryActionFilterer("123", "Doki Doki Literature Club", "Horror,Love"),
            EntryActionFilterer("124", "Danganronpa", "Visual novel"),
        ]

        self.oneAction = [
            EntryActionFilterer("123", "Doki Doki Literature Club", "Horror,Love"),
            EntryActionFilterer("12346", "Mirrors Edge", "Action,Suspense"),
            EntryActionFilterer("124", "Danganronpa", "Visual novel"),
        ]
        
        self.filterer = ActionFilterer()

    def testAllAction(self):
        result = self.filterer.filterBatch(self.allAction)
        ids = [entry._id for entry in result]
        expectedIds = ["12345", "12346", "12347"]

        self.assertEqual(len(result), len(self.allAction))
        self.assertEqual(ids, expectedIds)

    def testNoneAction(self):
        result = self.filterer.filterBatch(self.noneAction)
        self.assertEqual(len(result), 0)

    def testOneAction(self):
        result = self.filterer.filterBatch(self.oneAction)
        ids = [entry._id for entry in result]
        expectedIds = ["12346"]
        self.assertEqual(len(result), 1)
        self.assertEqual(ids, expectedIds)

 
if __name__ == '__main__':
    unittest.main()
