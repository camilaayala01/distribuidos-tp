import unittest
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from entryParsing.entryNameAvgPlaytime import EntryNameAvgPlaytime

class TestEntrySorterTopFinder(unittest.TestCase):
    def setUp(self):
        self.entry1 = EntryNameReviewCount("Fallout", 67020)
        self.entry2 = EntryNameReviewCount("Counter Strike", 120000000)
        self.entry3 = EntryNameReviewCount("Pepito y sus amigos", 15)

        self.entry4 = EntryNameAvgPlaytime("LOL", 15)

    def testSerializeAndDeserializeReviewCount(self):
        serialized = self.entry1.serialize()
        expectedLen = 1 + len(self.entry1._name.encode()) + 4
        deserialized = EntryNameReviewCount.deserialize(serialized)
        self.assertEqual(len(serialized), expectedLen)
        self.assertEqual(deserialized[0]._name, self.entry1._name)
        self.assertEqual(deserialized[0]._reviewCount, self.entry1._reviewCount)

    def testSerializeAndDeserializeAvgPlaytime(self):
        serialized = self.entry4.serialize()
        expectedLen = 1 + len(self.entry4._name.encode()) + 4
        deserialized = EntryNameAvgPlaytime.deserialize(serialized)
        self.assertEqual(len(serialized), expectedLen)
        self.assertEqual(deserialized[0]._name, self.entry4._name)
        self.assertEqual(deserialized[0]._avgPlaytime, self.entry4._avgPlaytime)

    def testSort(self):
        entries = [self.entry1, self.entry2, self.entry3]
        sortedEntries = EntryNameReviewCount.sort(entries, True)
        self.assertEqual(sortedEntries[0]._name, "Counter Strike")
        self.assertEqual(sortedEntries[1]._name, "Fallout")
        self.assertEqual(sortedEntries[2]._name, "Pepito y sus amigos")

        
    
if __name__ == "__main__":
    unittest.main()
