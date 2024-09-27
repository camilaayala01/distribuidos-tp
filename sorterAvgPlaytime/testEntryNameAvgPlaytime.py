import unittest

from entryNameAvgPlaytime import EntryNameAvgPlaytime

class TestEntryNameAvgPlaytime(unittest.TestCase):
    def setUp(self):
        self.entry1 = EntryNameAvgPlaytime("Fallout", 67020)
        self.entry2 = EntryNameAvgPlaytime("Counter Strike", 120000000)
        self.entry3 = EntryNameAvgPlaytime("Pepito y sus amigos", 15)
        
    def test_serialize(self):
        serialized = self.entry1.serialize()
        expectedLen = 1 + len(self.entry1._name.encode()) + 4
        self.assertEqual(len(serialized), expectedLen)

    def test_serialize_and_deserialize(self):
        serialized = self.entry1.serialize()
        expectedLen = 1 + len(self.entry1._name.encode()) + 4
        deserialized = EntryNameAvgPlaytime.deserialize(serialized)
        self.assertEqual(len(serialized), expectedLen)
        self.assertEqual(deserialized[0]._name, self.entry1._name)
        self.assertEqual(deserialized[0]._avgPlaytime, self.entry1._avgPlaytime)

    def test_sort(self):
        entries = [self.entry1, self.entry2, self.entry3]
        sorted_entries = EntryNameAvgPlaytime.sort(entries)
        self.assertEqual(sorted_entries[0]._name, "Counter Strike")
        self.assertEqual(sorted_entries[1]._name, "Fallout")
        self.assertEqual(sorted_entries[2]._name, "Pepito y sus amigos")
        
if __name__ == "__main__":
    unittest.main()
