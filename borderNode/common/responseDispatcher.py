import logging
import os
from threading import Event
from .borderCommunication import BorderNodeCommunication
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.common.messageType import MessageType
from internalCommunication.internalCommunication import InternalCommunication
from internalCommunication.internalMessageType import InternalMessageType

class ResponseDispatcher:
    def __init__(self, borderCommunication: BorderNodeCommunication, stopEvent: Event):
        self._communication = borderCommunication
        self._internalCommunication = InternalCommunication(os.getenv('DISP'))
        self._stopEvent = stopEvent

    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)
    
    def stop(self):
        self._internalCommunication.stop()

    def sendQueryToClient(self, body):
        if self._stopEvent.is_set():
            self.stop()
        header, _ = HeaderWithQueryNumber.deserialize(body)
        self._communication.sendToClient(clientId=header.getClient(), data=MessageType.QUERY_RESPONSE.serialize() + body)
        logging.info(f'action: sending query info to client | result: success')

    def handleMessage(self, ch, method, _properties, body):
        if self._stopEvent.is_set():
            self.stop()
        msgType, msg = InternalMessageType.deserialize(body)
        match msgType:
            case InternalMessageType.DATA_TRANSFER:
                self.sendQueryToClient(msg)
            case InternalMessageType.CLIENT_FLUSH:
                return
            case InternalMessageType.SHUTDOWN:
                self.stop()
        ch.basic_ack(delivery_tag = method.delivery_tag)