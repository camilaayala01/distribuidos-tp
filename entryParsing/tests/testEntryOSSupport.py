import unittest
from entryParsing.common.fieldParsing import BOOLEAN_LEN
from entryParsing.entryOSSupport import EntryOSSupport

class TestEntryOsSupport(unittest.TestCase):
    def setUp(self):
        self._entry = EntryOSSupport(True, False, True)
        
    def testSerialize(self):
        serialized = self._entry.serialize()
        expectedLen = 3 * BOOLEAN_LEN
        self.assertEqual(len(serialized), expectedLen)

    def testSerializeAndDeserialize(self):
        serialized = self._entry.serialize()
        deserialized = EntryOSSupport.deserialize(serialized)
        self.assertTrue(deserialized[0]._windows)
        self.assertFalse(deserialized[0]._mac)
        self.assertTrue(deserialized[0]._linux)

        
if __name__ == "__main__":
    unittest.main()
