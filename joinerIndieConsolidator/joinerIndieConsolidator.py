import os
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from joinerConsolidator.joinerConsolidator import JoinerConsolidator

class JoinerIndiePositiveConsolidator(JoinerConsolidator):
    
    def __init__(self): 
        super().__init__(type=os.getenv('CONS_JOIN_INDIE_POS_REV'), nextNodeCount=os.getenv('SORT_INDIE_POS_REV_COUNT'), 
                         priorNodeCount=os.getenv('JOIN_INDIE_POS_REV_COUNT'), entriesType=EntryNameReviewCount)

    def handleSending(self, header: HeaderWithSender, data: bytes):
        correspondingNode = self._currFragment % self._nextNodeCount
        if not self._tracker.isDone():
            self._internalCommunication.sendToPositiveReviewsSorter(str(correspondingNode), header.getHeaderSerialized() + data)
            return
        
        # send to all at least an empty payload so they know we've reached eof
        for node in range(self._nextNodeCount):
            if node == correspondingNode:
                self._internalCommunication.sendToPositiveReviewsSorter(str(node), header.getHeaderSerialized() + data)
            else:
                self._internalCommunication.sendToPositiveReviewsSorter(str(node), header.getHeaderSerialized())
    