import unittest
from entryParsing.entryAppIDReviewCount import EntryAppIDReviewCount
from entryParsing.common.fieldLen import APP_ID_LEN, COUNT_LEN

class TestEntryAppID(unittest.TestCase):
    def setUp(self):
        self._entry1 = EntryAppIDReviewCount("1", 1)
        self._entry2 = EntryAppIDReviewCount("2", 2)
        self._entry3 = EntryAppIDReviewCount("3", 3)
        
    def testSerialize(self):
        serialized = self._entry1.serialize()
        expectedLen = APP_ID_LEN + len(self._entry1._appID.encode()) + COUNT_LEN
        self.assertEqual(len(serialized), expectedLen)

    def testSerializeAndDeserialize(self):
        serialized = self._entry1.serialize() + self._entry2.serialize() + self._entry3.serialize()
        expectedLen = APP_ID_LEN + len(self._entry1._appID.encode()) + COUNT_LEN + APP_ID_LEN + len(self._entry2._appID.encode()) + COUNT_LEN + APP_ID_LEN + len(self._entry3._appID.encode()) + COUNT_LEN
        deserialized = EntryAppIDReviewCount.deserialize(serialized)
        self.assertEqual(len(serialized), expectedLen)
        self.assertEqual(deserialized[0]._appID, self._entry1._appID)
        self.assertEqual(deserialized[0]._reviewCount, self._entry1._reviewCount)
        self.assertEqual(deserialized[1]._appID, self._entry2._appID)
        self.assertEqual(deserialized[1]._reviewCount, self._entry2._reviewCount)
        self.assertEqual(deserialized[2]._appID, self._entry3._appID)
        self.assertEqual(deserialized[2]._reviewCount, self._entry3._reviewCount)
        self.assertEqual(len(deserialized), 3)

if __name__ == "__main__":
    unittest.main()
