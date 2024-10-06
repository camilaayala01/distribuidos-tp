import os
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.entryName import EntryName
from joiner.common.joinerConsolidator import JoinerConsolidator

class JoinerStreamConsolidator(JoinerConsolidator):
    
    def __init__(self): 
        super().__init__(type=os.getenv('CONS_JOIN_STREAM'), nextNodeCount=1, 
                         priorNodeCount=os.getenv('JOIN_ENG_COUNT_MORE_REV_COUNT'), entriesType=EntryName)

    def handleSending(self, _header: HeaderWithSender, data: bytes):
        self._internalCommunication.sendToDispatcher(self.getHeaderSerialized() + data)