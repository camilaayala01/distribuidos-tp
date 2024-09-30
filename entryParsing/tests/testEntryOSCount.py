import unittest
from entryParsing.entryAppIDReviewCount import COUNT_LEN
from entryParsing.entryOSCount import EntryOSCount

class TestEntryOSCount(unittest.TestCase):
    def setUp(self):
        self._entry = EntryOSCount(10, 600000, 500)
        
    def testSerialize(self):
        serialized = self._entry.serialize()
        expectedLen = 3 * COUNT_LEN
        self.assertEqual(len(serialized), expectedLen)

    def testSerializeAndDeserialize(self):
        serialized = self._entry.serialize()
        deserialized = EntryOSCount.deserialize(serialized)
        self.assertEqual(deserialized._windows, 10)
        self.assertEqual(deserialized._mac, 600000)
        self.assertEqual(deserialized._linux, 500)