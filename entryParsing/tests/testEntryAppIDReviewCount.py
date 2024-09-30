import unittest

from entryParsing.common.entryAppIDReviewCount import EntryAppIDReviewCount


class TestEntryAppID(unittest.TestCase):
    def setUp(self):
        self._entry1 = EntryAppIDReviewCount("1", 1)
        self._entry2 = EntryAppIDReviewCount("2", 2)
        self._entry3 = EntryAppIDReviewCount("3", 3)
        
    def testSerialize(self):
        serialized = self._entry1.serialize()
        expectedLen = 1 + len(self._entry1._appID.encode()) + 1
        self.assertEqual(len(serialized), expectedLen)

    def testSerializeAndDeserialize(self):
        serialized = self._entry1.serialize() + self._entry2.serialize() + self._entry3.serialize()
        expectedLen = 1 + len(self._entry1._appID.encode()) + 1 +  1 + len(self._entry2._appID.encode())  + 1 + 1 + len(self._entry3._appID.encode()) + 1
        deserialized = EntryAppIDReviewCount.deserialize(serialized)
        self.assertEqual(len(serialized), expectedLen)
        self.assertEqual(deserialized[0]._appID, self._entry1._appID)
        self.assertEqual(deserialized[0]._count, self._entry1._count)
        self.assertEqual(deserialized[1]._appID, self._entry2._appID)
        self.assertEqual(deserialized[1]._count, self._entry2._count)
        self.assertEqual(deserialized[2]._appID, self._entry3._appID)
        self.assertEqual(deserialized[2]._count, self._entry3._count)
        self.assertEqual(len(deserialized), 3)

        
if __name__ == "__main__":
    unittest.main()
