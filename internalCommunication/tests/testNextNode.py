import os
import unittest
from entryParsing.entryAppID import EntryAppID
from entryParsing.entryAppIDNameReviewCount import EntryAppIDNameReviewCount
from internalCommunication.common.nextNode import NextNode
from internalCommunication.directSend import ShardingAttribute

class TestNextNode(unittest.TestCase):
    def setUp(self):
        os.environ['ENTRY_PATH']='entryParsing'

    def testNextNodeOnlyOneNoShardingAttribute(self):
        nextNodes = NextNode.parseNodes("GROUPER")
        self.assertEqual(len(nextNodes), 1)
        self.assertEqual(nextNodes[0]._queueName, "GROUPER")
        self.assertEqual(nextNodes[0]._count, None)
        self.assertEqual(nextNodes[0]._shardingAttribute, None)
    
    def testNextNodeOnlyOneWithShardingAttribute(self):
        nextNodes = NextNode.parseNodes("GROUPER,2,1")
        self.assertEqual(len(nextNodes), 1)
        self.assertEqual(nextNodes[0]._queueName, "GROUPER")
        self.assertEqual(nextNodes[0]._count, 2)
        self.assertEqual(nextNodes[0]._shardingAttribute, ShardingAttribute(1))

    def testNextNodeMoreThanOneNoShardingAttribute(self):
        nextNodes = NextNode.parseNodes("GROUPER;JOINER")
        self.assertEqual(len(nextNodes), 2)
        self.assertEqual(nextNodes[0]._queueName, "GROUPER")
        self.assertEqual(nextNodes[0]._count, None)
        self.assertEqual(nextNodes[0]._shardingAttribute, None)
        self.assertEqual(nextNodes[1]._queueName, "JOINER")
        self.assertEqual(nextNodes[0]._count, None)
        self.assertEqual(nextNodes[1]._shardingAttribute, None)
    
    def testNextNodeMoreThanOneBothShardingAttributes(self):
        nextNodes = NextNode.parseNodes("GROUPER,2,0;JOINER,3,1")
        
        self.assertEqual(len(nextNodes), 2)
        self.assertEqual(nextNodes[0]._queueName, "GROUPER")
        self.assertEqual(nextNodes[0]._count, 2)
        self.assertEqual(nextNodes[0]._shardingAttribute, ShardingAttribute(0))

        self.assertEqual(nextNodes[1]._queueName, "JOINER")
        self.assertEqual(nextNodes[1]._count, 3)
        self.assertEqual(nextNodes[1]._shardingAttribute, ShardingAttribute(1))

    def testNextNodeMoreThanOneSomeShardingAttribute(self):
        nextNodes = NextNode.parseNodes("GROUPER;JOINER,3,1")
        
        self.assertEqual(len(nextNodes), 2)
        self.assertEqual(nextNodes[0]._queueName, "GROUPER")
        self.assertEqual(nextNodes[0]._count, None)
        self.assertEqual(nextNodes[0]._shardingAttribute, None)

        self.assertEqual(nextNodes[1]._queueName, "JOINER")
        self.assertEqual(nextNodes[1]._count, 3)
        self.assertEqual(nextNodes[1]._shardingAttribute, ShardingAttribute(1))
    
    def testNextVariedWithEntryTypes(self):
        nextNodes = NextNode.parseNodes("GROUPER;JOINER,3,1", "EntryAppID;EntryAppIDNameReviewCount")
        self.assertEqual(len(nextNodes), 2)
        self.assertEqual(nextNodes[0]._entryType, EntryAppID)
        self.assertEqual(nextNodes[1]._entryType, EntryAppIDNameReviewCount)

if __name__ == "__main__":
    unittest.main()