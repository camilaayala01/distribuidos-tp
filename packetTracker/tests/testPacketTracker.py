import unittest
from entryParsing.common.header import Header
from ..packetTracker import PacketTracker
from ..defaultTracker import DefaultTracker

class TestPacketTracker(unittest.TestCase):
    def setUp(self):
        # this tracker expects even numbers
        self.tracker = PacketTracker(nodesInCluster=2, module=0)
        self.defaultTracker = DefaultTracker()
    
    def testisDuplicateBiggerThanPriorBiggest(self):
        header = Header(fragment=5, eof=False)
        self.tracker._biggestFragment = 3
        
        # bigger than the biggest received
        self.assertFalse(self.tracker.isDuplicate(header))
    
    def testIsDuplicateSmallerThanPriorBiggest(self):
        header = Header(fragment=2, eof=False)
        self.tracker._biggestFragment = 5
        self.tracker._pending = set([2, 3])
        
        # 2 is in pending set, not a duplicate
        self.assertFalse(self.tracker.isDuplicate(header))
        
        # delete manually just to test duplicates
        self.tracker._pending.discard(2)
        self.assertTrue(self.tracker.isDuplicate(header))
    
    def testUpdateWithNewFragmentBiggerInDefault(self):
        header = Header(fragment=5, eof=False)
        self.defaultTracker._biggestFragment = 2
        
        self.defaultTracker.update(header)
        
        self.assertEqual(self.defaultTracker._biggestFragment, 5)
        self.assertIn(3, self.defaultTracker._pending)
        self.assertIn(4, self.defaultTracker._pending)
        self.assertFalse(self.defaultTracker._receivedEnd)
    
    def testUpdateWithNewFragmentBigger(self):
        header = Header(fragment=6, eof=False)
        self.tracker._biggestFragment=2
        
        self.tracker.update(header)
        
        self.assertEqual(self.tracker._biggestFragment, 6)
        self.assertNotIn(2, self.tracker._pending)
        self.assertNotIn(3, self.tracker._pending)
        self.assertIn(4, self.tracker._pending)
        self.assertNotIn(5, self.tracker._pending)
        self.assertFalse(self.tracker._receivedEnd)
    
    def testUpdateEof(self):
        header = Header(fragment=8, eof=True)
        self.tracker._biggestFragment = 6
        
        self.tracker.update(header)
        self.assertEqual(self.tracker._biggestFragment, 8)
        self.assertEqual(len(self.tracker._pending), 0)
        self.assertTrue(self.tracker._receivedEnd)
    
    def testUpdateDiscardPending(self):
        header = Header(fragment=2, eof=False)
        self.tracker._biggestFragment=6
        self.tracker._pending = set([2, 4])
        
        self.tracker.update(header)
        self.assertNotIn(2, self.tracker._pending)
    
    def testIsDoneWithPendingAndNotEnd(self):
        self.tracker._pending = set([2])
        self.tracker._receivedEnd = False
        
        self.assertFalse(self.tracker.isDone())
    
    def testisDoneWithNoPendingButNotEnd(self):
        self.tracker._pending = set()
        self.tracker._receivedEnd = False
        
        self.assertFalse(self.tracker.isDone())

    def testisDoneWithNoPendingAndEnd(self):
        self.tracker._pending = set()
        self.tracker._receivedEnd = True
        
        self.assertTrue(self.tracker.isDone())

if __name__ == '__main__':
    unittest.main()