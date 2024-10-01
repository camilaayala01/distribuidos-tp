import unittest
from entryParsing.common.header import EOF_FLAG_LEN, FRAGMENT_LEN, Header
from entryParsing.entryOSCount import EntryOSCount

class TestHeader(unittest.TestCase):
    def setUp(self):
        self._entrySome = Header(2, False)
        self._entryLast = Header(10, True)
        
    def testSerialize(self):
        serialized = self._entrySome.serialize()
        expectedLen = FRAGMENT_LEN + EOF_FLAG_LEN
        self.assertEqual(len(serialized), expectedLen)

    def testSerializeAndDeserialize(self):
        serializedSome = self._entrySome.serialize()
        serializedLast = self._entryLast.serialize()
        deserializedSome, _ = Header.deserialize(serializedSome)
        deserializedLast, _ = Header.deserialize(serializedLast)
        self.assertEqual(deserializedSome._fragment, 2)
        self.assertFalse(deserializedSome._eof)
        self.assertEqual(deserializedLast._fragment, 10)
        self.assertTrue(deserializedLast._eof)

    def testSerializeAndDeserializeWithExtraData(self):
        serializedHeader = self._entryLast.serialize()
        serializedEntryOsCount = EntryOSCount(10, 600000, 500).serialize()
        data = serializedHeader + serializedEntryOsCount
        deserializedHeader, rest = Header.deserialize(data)
        deserializedOsCount = EntryOSCount.deserialize(rest)
        self.assertEqual(deserializedHeader._fragment, 10)
        self.assertTrue(deserializedHeader._eof)
        self.assertEqual(deserializedOsCount._windows, 10)
        self.assertEqual(deserializedOsCount._mac, 600000)
        self.assertEqual(deserializedOsCount._linux, 500)