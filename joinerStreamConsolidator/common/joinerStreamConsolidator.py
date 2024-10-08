import os
import logging
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.entryName import EntryName
from joiner.common.joinerConsolidator import JoinerConsolidator

class JoinerStreamConsolidator(JoinerConsolidator):
    
    def __init__(self): 
        super().__init__(type=os.getenv('CONS_JOIN_STREAM'), nextNodeCount=1, 
                         priorNodeCount=int(os.getenv('JOIN_ENG_COUNT_MORE_REV_COUNT')), entriesType=EntryName)

    def getHeaderSerialized(self):
        return HeaderWithQueryNumber(fragment=self._currFragment, eof=self._tracker.isDone(), queryNumber=4).serialize()
    
    def handleSending(self, header: HeaderWithQueryNumber, data: bytes):
        self._internalCommunication.sendToDispatcher(self.getHeaderSerialized() + data)
        logging.info(f'action: sending to dispatcher batch | {header} | result: success')