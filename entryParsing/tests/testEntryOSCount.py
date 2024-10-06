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
        deserialized = EntryOSCount.deserialize(serialized)
        self.assertEqual(deserialized._windows, 10)
        self.assertEqual(deserialized._mac, 600000)
        self.assertEqual(deserialized._linux, 500)
        self.assertEqual(deserialized._total, 600200)