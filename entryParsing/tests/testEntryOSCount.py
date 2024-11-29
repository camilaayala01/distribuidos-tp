import unittest
from entryParsing.common.fieldLen import COUNT_LEN
from entryParsing.entryOSCount import EntryOSCount

class TestEntryOSCount(unittest.TestCase):
    def setUp(self):
        self._entry = EntryOSCount(10, 600000, 500, 600200)
        
    def testSerialize(self):
        serialized = self._entry.serialize()
        expectedLen = 4 * COUNT_LEN
        self.assertEqual(len(serialized), expectedLen)

    def testSerializeAndDeserialize(self):
        serialized = self._entry.serialize()
        deserialized = EntryOSCount.deserialize(serialized)[0]
        self.assertEqual(deserialized._windowsCount, 10)
        self.assertEqual(deserialized._macCount, 600000)
        self.assertEqual(deserialized._linuxCount, 500)
        self.assertEqual(deserialized._totalCount, 600200)
    
if __name__ == "__main__":
    unittest.main()
