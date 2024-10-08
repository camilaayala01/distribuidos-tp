import os
import logging
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from joiner.common.joinerConsolidator import JoinerConsolidator

class JoinerIndiePositiveConsolidator(JoinerConsolidator):
    def __init__(self): 
        super().__init__(type=os.getenv('CONS_JOIN_INDIE_POS_REV'), nextNodeCount=int(os.getenv('SORT_INDIE_POS_REV_COUNT')), 
                         priorNodeCount=int(os.getenv('JOIN_INDIE_POS_REV_COUNT')), entriesType=EntryNameReviewCount)

    def handleSending(self, header: HeaderWithSender, data: bytes):
        correspondingNode = self._currFragment % self._nextNodeCount
        if not self._tracker.isDone():
            self._internalCommunication.sendToPositiveReviewsSorter(str(correspondingNode), self.getHeaderSerialized() + data)
            logging.info("action: sending batch to positive reviews sorter | result: success")
            return
        
        # send to all at least an empty payload so they know we've reached eof
        for node in range(self._nextNodeCount):
            if node == correspondingNode:
                self._internalCommunication.sendToPositiveReviewsSorter(str(node), self.getHeaderSerialized() + data)
            else:
                self._internalCommunication.sendToPositiveReviewsSorter(str(node), self.getHeaderSerialized())

        logging.info("action: sending EOF to positive reviews sorter | result: success")
    