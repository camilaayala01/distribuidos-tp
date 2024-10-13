from entryParsing.entry import EntryInterface
from entryParsing.entryAppID import EntryAppID
from entryParsing.common.header import Header
from grouper.common.grouperTypes import GrouperType
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.utils import initializeLog
import logging
import os

from sendingStrategy.common.utils import createStrategiesFromNextNodes

class Grouper:
    def __init__(self):
        initializeLog()
        self._grouperType = GrouperType(int(os.getenv('GROUPER_TYPE')))
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'))
        self._sendingStrategies = createStrategiesFromNextNodes()

    def stop(self, _signum, _frame):
        self._internalCommunication.stop()
    
    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)
    
    def _sendToNext(self, header: Header, batch: list[EntryInterface]):
        for strategy in self._sendingStrategies:
            newHeader = self._grouperType.getResultingHeader(header)
            strategy.send(self._internalCommunication, newHeader, batch)

    def handleMessage(self, ch, method, properties, body):
        header, data = self._grouperType.headerType().deserialize(body)
        logging.info(f'action: received batch | {header} | result: success')
        entries = self._grouperType.entryType().deserialize(data)
        result = self._grouperType.getResults(entries)
        self._sendToNext(header, result)
        ch.basic_ack(delivery_tag = method.delivery_tag)