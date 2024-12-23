import os
from entryParsing.headerInterface import HeaderInterface
from entryParsing.messagePart import MessagePartInterface
from healthcheckAnswerController.healthcheckAnswerController import HealthcheckAnswerController
from internalCommunication.common.utils import createStrategiesFromNextNodes
from internalCommunication.internalMessageType import InternalMessageType
from .filtererTypes import FiltererType
from internalCommunication.internalCommunication import InternalCommunication
import logging
from entryParsing.common.utils import getReducedEntryTypeFromEnv, getHeaderTypeFromEnv, initializeLog


class Filterer:
    def __init__(self):
        initializeLog()
        self._filtererType = FiltererType(int(os.getenv('FILTERER_TYPE')))
        self._entryType = getReducedEntryTypeFromEnv()
        self._headerType = getHeaderTypeFromEnv()
        self._internalCommunication = InternalCommunication(os.getenv('LISTENING_QUEUE'))
        self._sendingStrategies = createStrategiesFromNextNodes()
        self._healthcheckAnswerController = HealthcheckAnswerController()
        self._healthcheckAnswerController.execute()      

    def _sendToNext(self, header: HeaderInterface, batch: list[MessagePartInterface]):
        for strategy in self._sendingStrategies:
            strategy.sendData(self._internalCommunication, header, batch)

    def stop(self, _signum, _frame):
        self._internalCommunication.stop()
        self._healthcheckAnswerController.stop()

    def handleDataMessage(self, body):
        header, data = self._headerType.deserialize(body)
        entries = self._entryType.deserialize(data)
        filteredEntries = self.filterBatch(entries)
        self._sendToNext(header, filteredEntries)
    
    def handleMessage(self, ch, method, _properties, body):
        msgType, msg = InternalMessageType.deserialize(body)
        match msgType:
            case InternalMessageType.DATA_TRANSFER:
                self.handleDataMessage(msg)
            case InternalMessageType.CLIENT_FLUSH:
                for strategy in self._sendingStrategies:
                    strategy.sendFlush(middleware=self._internalCommunication, clientId=msg)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)

    def filterBatch(self, batch: list[MessagePartInterface]) -> list[MessagePartInterface]:
        return [entry for entry in batch if self._filtererType.executeCondition(entry)]