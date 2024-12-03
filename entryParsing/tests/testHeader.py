import unittest
import uuid
from entryParsing.headerInterface import HeaderInterface
from entryParsing.headerInterface import HeaderWithSender
from entryParsing.entryOSCount import EntryOSCount

class TestHeader(unittest.TestCase):
    def setUp(self):
        clientId = uuid.UUID('6bbe9f2a-1c58-4951-a92c-3f2b05147a29').bytes
        self._entrySome = HeaderInterface(_clientId = clientId, _fragment = 2, _eof = False)
        self._entryLast = HeaderInterface(_clientId= clientId, _fragment=10, _eof = True)
        self._headerWithSender = HeaderWithSender(clientId, 2, False, 1)

    def testSerializeDefault(self):
        serialized = self._entrySome.serialize()
        self.assertEqual(len(serialized), HeaderInterface.size())

    def testSerializeWithSender(self):
        serialized = self._headerWithSender.serialize()
        self.assertEqual(len(serialized), HeaderWithSender.size())

    def testSerializeAndDeserializeHeader(self):
        serializedSome = self._entrySome.serialize()
        serializedLast = self._entryLast.serialize()
        deserializedSome, _ = HeaderInterface.deserialize(serializedSome)
        deserializedLast, _ = HeaderInterface.deserialize(serializedLast)
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
        deserializedHeader, rest = HeaderInterface.deserialize(data)
        deserializedOsCount = EntryOSCount.deserialize(rest)[0]
        self.assertEqual(deserializedHeader._fragment, 10)
        self.assertTrue(deserializedHeader._eof)
        self.assertEqual(deserializedOsCount._windowsCount, 10)
        self.assertEqual(deserializedOsCount._macCount, 600000)
        self.assertEqual(deserializedOsCount._linuxCount, 500)
        self.assertEqual(deserializedOsCount._totalCount, 600200)
    
if __name__ == "__main__":
    unittest.main()
