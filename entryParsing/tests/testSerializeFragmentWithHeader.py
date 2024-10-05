import os
import unittest
from unittest.mock import MagicMock, patch

from sorterConsolidatorActionPercentile.common.sorterConsolidatorActionPercentile import SorterConsolidatorActionPercentile
from ..common.headerWithSender import HeaderWithSender
from ..common.utils import serializeAndFragmentWithSender
from ..entryNameReviewCount import EntryNameReviewCount

class TestSerializeFragmentWithHeader(unittest.TestCase):
    @patch('internalCommunication.internalCommunication.InternalCommunication.__init__', MagicMock(return_value=None))
    def setUp(self):
        self.entriesEqual = [
            EntryNameReviewCount("Game A", 100),
            EntryNameReviewCount("Game B", 120),
            EntryNameReviewCount("Game C", 1100),
        ]
        os.environ['NODE_ID'] = '1'
        os.environ['CONS_SORT_PERC_NEG_REV'] = 'sorterAction'
        os.environ['SORT_INDIE_POS_REV'] = 'sorterIndie'
        os.environ['JOIN_PERC_NEG_REV_COUNT'] = '2'
        self.sorterAction = SorterConsolidatorActionPercentile()   

    def testSerializeDataWithSmallMaxDataBytes(self):
        self.sorterAction._partialTop = self.entriesEqual
        self.sorterAction._id = 1

        packets = serializeAndFragmentWithSender(15, self.sorterAction._partialTop, self.sorterAction._id)
        self.assertEqual(len(packets), 3)
        deserialized = []

        for pack in packets:
            header, _ = HeaderWithSender.deserialize(pack)
            deserialized.append(header)

        self.assertEqual(deserialized[0]._eof, False)
        self.assertEqual(deserialized[0]._fragment, 1)
        self.assertEqual(deserialized[1]._eof, False)
        self.assertEqual(deserialized[1]._fragment, 2)
        self.assertEqual(deserialized[2]._eof, True)
        self.assertEqual(deserialized[2]._fragment, 3)
        
    def testSerializeDataWithBigMaxDataBytes(self):
        self.sorterAction._partialTop = self.entriesEqual
        self.sorterAction._id = 1
        packets = serializeAndFragmentWithSender(1000, self.sorterAction._partialTop, self.sorterAction._id)
        self.assertEqual(len(packets), 1)
        header, _ = HeaderWithSender.deserialize(packets[0])

        self.assertEqual(header._eof, True)
        self.assertEqual(header._fragment, 1)

    def testSerializeDataWithExactMaxDataBytes(self):
        self.sorterAction._partialTop = self.entriesEqual
        entriesLen = 0
        for entry in self.sorterAction._partialTop:
            entriesLen += len(entry.serialize())

        self.sorterAction._id = 1
        packets = serializeAndFragmentWithSender(entriesLen, self.sorterAction._partialTop, self.sorterAction._id)
        self.assertEqual(len(packets), 1)
        header, _ = HeaderWithSender.deserialize(packets[0])

        self.assertEqual(header._eof, True)
        self.assertEqual(header._fragment, 1)