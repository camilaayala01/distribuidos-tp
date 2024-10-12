import unittest
from nextNode.nextNode import NextNode
from sendingStrategy.directSend import ShardingAttribute

class TestNextNode(unittest.TestCase):
    def testNextNodeOnlyOneNoShardingAttribute(self):
        nextNodes = NextNode.parse("GROUPER,2")
        self.assertEqual(len(nextNodes), 1)
        self.assertEqual(nextNodes[0]._queueName, "GROUPER")
        self.assertEqual(nextNodes[0]._nextNodeCount, "2")
        self.assertEqual(nextNodes[0]._shardingAttribute, None)
    
    def testNextNodeOnlyOneWithShardingAttribute(self):
        nextNodes = NextNode.parse("GROUPER,2,1")
        self.assertEqual(len(nextNodes), 1)
        self.assertEqual(nextNodes[0]._queueName, "GROUPER")
        self.assertEqual(nextNodes[0]._nextNodeCount, "2")
        self.assertEqual(nextNodes[0]._shardingAttribute, ShardingAttribute(1))

    def testNextNodeMoreThanOneNoShardingAttribute(self):
        nextNodes = NextNode.parse("GROUPER,2;JOINER,3")
        self.assertEqual(len(nextNodes), 2)
        self.assertEqual(nextNodes[0]._queueName, "GROUPER")
        self.assertEqual(nextNodes[0]._nextNodeCount, "2")
        self.assertEqual(nextNodes[0]._shardingAttribute, None)
        self.assertEqual(nextNodes[1]._queueName, "JOINER")
        self.assertEqual(nextNodes[1]._nextNodeCount, "3")
        self.assertEqual(nextNodes[1]._shardingAttribute, None)
    
    def testNextNodeMoreThanOneBothShardingAttributes(self):
        nextNodes = NextNode.parse("GROUPER,2,0;JOINER,3,1")
        
        self.assertEqual(len(nextNodes), 2)
        self.assertEqual(nextNodes[0]._queueName, "GROUPER")
        self.assertEqual(nextNodes[0]._nextNodeCount, "2")
        self.assertEqual(nextNodes[0]._shardingAttribute, ShardingAttribute(0))

        self.assertEqual(nextNodes[1]._queueName, "JOINER")
        self.assertEqual(nextNodes[1]._nextNodeCount, "3")
        self.assertEqual(nextNodes[1]._shardingAttribute, ShardingAttribute(1))

    def testNextNodeMoreThanOneSomeShardingAttribute(self):
        nextNodes = NextNode.parse("GROUPER,2;JOINER,3,1")
        
        self.assertEqual(len(nextNodes), 2)
        self.assertEqual(nextNodes[0]._queueName, "GROUPER")
        self.assertEqual(nextNodes[0]._nextNodeCount, "2")
        self.assertEqual(nextNodes[0]._shardingAttribute, None)

        self.assertEqual(nextNodes[1]._queueName, "JOINER")
        self.assertEqual(nextNodes[1]._nextNodeCount, "3")
        self.assertEqual(nextNodes[1]._shardingAttribute, ShardingAttribute(1))

if __name__ == "__main__":
    unittest.main()