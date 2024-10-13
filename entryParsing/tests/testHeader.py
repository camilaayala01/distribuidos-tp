import unittest
from entryParsing.common.header import Header
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.entryOSCount import EntryOSCount

class TestHeader(unittest.TestCase):
    def setUp(self):
        self._entrySome = Header(2, False)
        self._entryLast = Header(10, True)
        self._headerWithSender = HeaderWithSender(1, 2, False)

    def testSerializeDefault(self):
        serialized = self._entrySome.serialize()
        self.assertEqual(len(serialized), Header.size())

    def testSerializeWithSender(self):
        serialized = self._headerWithSender.serialize()
        self.assertEqual(len(serialized), HeaderWithSender.size())

    def testSerializeAndDeserializeHeader(self):
        serializedSome = self._entrySome.serialize()
        serializedLast = self._entryLast.serialize()
        deserializedSome, _ = Header.deserialize(serializedSome)
        deserializedLast, _ = Header.deserialize(serializedLast)
        self.assertEqual(deserializedSome._fragment, 2)
        self.assertFalse(deserializedSome._eof)
        self.assertEqual(deserializedLast._fragment, 10)
        self.assertTrue(deserializedLast._eof)

    def testSerializeAndDeserializeHeaderWithSender(self):
        serialized = self._headerWithSender.serialize()
        deserialized, _ = HeaderWithSender.deserialize(serialized)
        self.assertEqual(deserialized._sender, 1)
        self.assertEqual(deserialized._fragment, 2)
        self.assertFalse(deserialized._eof)

    def testSerializeAndDeserializeWithExtraData(self):
        serializedHeader = self._entryLast.serialize()
        serializedEntryOsCount = EntryOSCount(10, 600000, 500, 600200).serialize()
        data = serializedHeader + serializedEntryOsCount
        deserializedHeader, rest = Header.deserialize(data)
        deserializedOsCount = EntryOSCount.deserialize(rest)
        self.assertEqual(deserializedHeader._fragment, 10)
        self.assertTrue(deserializedHeader._eof)
        self.assertEqual(deserializedOsCount._windows, 10)
        self.assertEqual(deserializedOsCount._mac, 600000)
        self.assertEqual(deserializedOsCount._linux, 500)
        self.assertEqual(deserializedOsCount._total, 600200)
    
if __name__ == "__main__":
    unittest.main()
