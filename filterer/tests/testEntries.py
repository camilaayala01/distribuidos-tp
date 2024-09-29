import unittest
from datetime import datetime
from ..actionFilterer.entryActionFilterer import EntryActionFilterer
from ..englishFilterer.entryEnglishFilterer import EntryEnglishFilterer
from ..dateFilterer.entryDateFilterer import EntryDateFilterer
from ..indieFilterer.entryIndieFilterer import EntryIndieFilterer

class TestEntries(unittest.TestCase):
    def setUp(self):
        self.entry1 = EntryActionFilterer("12345", "Doom Eternal", ["Shooter", "Action"])
        self.entry2 = EntryEnglishFilterer("12346", "Dress to Impress", "Este juego devoro slay mama work")
        self.entry3 = EntryIndieFilterer("12453", "Undertale", ["Fantasy", "Horror"], datetime.strptime("2017-01-02", "%Y-%m-%d"), 12341231)
        self.entry4 = EntryDateFilterer("League of Legends", datetime.strptime("2009-12-12", "%Y-%m-%d"), 123123123)

    def testSerializeAndDeserializeActionEntry(self):
        serialized = self.entry1.serialize()
        expectedLen = 1 + len(self.entry1._name.encode()) + 1 + len(self.entry1._id.encode()) + 1 + len(','.join(self.entry1._genres).encode())
        deserialized = EntryActionFilterer.deserializeEntry(0, serialized)
        self.assertEqual(len(serialized), expectedLen)
        self.assertEqual(deserialized[0]._name, self.entry1._name)
        self.assertEqual(deserialized[0]._id, self.entry1._id)
        self.assertEqual(deserialized[0]._genres, ','.join(self.entry1._genres))

    def testSerializeAndDeserializeEnglishEntry(self):
        serialized = self.entry2.serialize()
        expectedLen = 1 + len(self.entry2._id.encode()) + 1 + len(self.entry2._name.encode()) + 2 + len(self.entry2._reviewText.encode()) 
        deserialized = EntryEnglishFilterer.deserializeEntry(0, serialized)
        self.assertEqual(len(serialized), expectedLen)
        self.assertEqual(deserialized[0]._name, self.entry2._name)
        self.assertEqual(deserialized[0]._id, self.entry2._id)
        self.assertEqual(deserialized[0]._reviewText, self.entry2._reviewText)

    def testSerializeAndDeserializeIndieEntry(self):
        serialized = self.entry3.serialize()
        expectedLen = 1 + len(self.entry3._id.encode()) + 1 + len(self.entry3._name.encode()) + 1 + len(','.join(self.entry3._genres).encode()) + 10 + 4
        deserialized = EntryIndieFilterer.deserializeEntry(0, serialized)
        self.assertEqual(len(serialized), expectedLen) 
        self.assertEqual(deserialized[0]._name, self.entry3._name)
        self.assertEqual(deserialized[0]._id, self.entry3._id)
        self.assertEqual(deserialized[0]._genres, ','.join(self.entry3._genres))
        self.assertEqual(deserialized[0]._releaseDate, self.entry3._releaseDate, "%Y-%m-%d")
        self.assertEqual(deserialized[0]._avgPlaytimeForever, self.entry3._avgPlaytimeForever)

    def testSerializeAndDeserializeDateEntry(self):
        serialized = self.entry4.serialize()
        expectedLen = 1 + len(self.entry4._name.encode()) + 10 + 4
        deserialized = EntryDateFilterer.deserializeEntry(0, serialized)
        self.assertEqual(len(serialized), expectedLen) 
        self.assertEqual(deserialized[0]._name, self.entry4._name)
        self.assertEqual(deserialized[0]._releaseDate, self.entry4._releaseDate)
        self.assertEqual(deserialized[0]._avgPlaytimeForever, self.entry4._avgPlaytimeForever)

     
if __name__ == "__main__":
    unittest.main()
