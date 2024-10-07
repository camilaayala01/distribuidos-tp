import unittest
from entryParsing.entryAppID import EntryAppID
from entryParsing.common.fieldLen import APP_ID_LEN

class TestEntryAppID(unittest.TestCase):
    def setUp(self):
        self._entry1 = EntryAppID("1")
        self._entry2 = EntryAppID("2")
        self._entry3 = EntryAppID("1")
        
    def testSerialize(self):
        serialized = self._entry1.serialize()
        expectedLen = APP_ID_LEN + len(self._entry1._appID.encode())
        self.assertEqual(len(serialized), expectedLen)

    def testSerializeAndDeserialize(self):
        serialized = self._entry1.serialize() + self._entry2.serialize() + self._entry3.serialize()
        expectedLen = APP_ID_LEN + len(self._entry1._appID.encode()) +  APP_ID_LEN + len(self._entry2._appID.encode()) + APP_ID_LEN + len(self._entry3._appID.encode())
        deserialized = EntryAppID.deserialize(serialized)
        self.assertEqual(len(serialized), expectedLen)
        self.assertEqual(deserialized[0]._appID, self._entry1._appID)
        self.assertEqual(deserialized[1]._appID, self._entry2._appID)
        self.assertEqual(deserialized[2]._appID, self._entry3._appID)
        self.assertEqual(len(deserialized), 3)

        
if __name__ == "__main__":
    unittest.main()
