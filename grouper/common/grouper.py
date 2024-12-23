from entryParsing.headerInterface import HeaderInterface
from entryParsing.messagePart import MessagePartInterface
from healthcheckAnswerController.healthcheckAnswerController import HealthcheckAnswerController
from internalCommunication.common.utils import createStrategiesFromNextNodes
from internalCommunication.internalMessageType import InternalMessageType
from .grouperTypes import GrouperType
from internalCommunication.internalCommunication import InternalCommunication
from entryParsing.common.utils import getReducedEntryTypeFromEnv, getHeaderTypeFromEnv, initializeLog
import logging
import os


class Grouper:
    def __init__(self):
        initializeLog()
        self._grouperType = GrouperType(int(os.getenv('GROUPER_TYPE')))
        self._entryType = getReducedEntryTypeFromEnv()
        self._headerType = getHeaderTypeFromEnv()
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'))
        self._sendingStrategies = createStrategiesFromNextNodes()
        self._healthcheckAnswerController = HealthcheckAnswerController()
        self._healthcheckAnswerController.execute()      

    def stop(self, _signum, _frame):
        self._internalCommunication.stop()
        self._healthcheckAnswerController.stop()
    
    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)
    
    def _sendToNext(self, header: HeaderInterface, batch: list[MessagePartInterface]):
        for strategy in self._sendingStrategies:
            strategy.sendData(self._internalCommunication, header, batch)

    def handleDataMessage(self, body):
        header, data = self._headerType.deserialize(body)
        entries = self._entryType.deserialize(data)
        result = self._grouperType.getResults(entries)
        self._sendToNext(header, result)

    def handleMessage(self, ch, method, _properties, body):
        msgType, msg = InternalMessageType.deserialize(body)
        match msgType:
            case InternalMessageType.DATA_TRANSFER:
                self.handleDataMessage(msg)
            case InternalMessageType.CLIENT_FLUSH:
                for strategy in self._sendingStrategies:
                    strategy.sendFlush(middleware=self._internalCommunication, clientId=msg)
        ch.basic_ack(delivery_tag = method.delivery_tag)