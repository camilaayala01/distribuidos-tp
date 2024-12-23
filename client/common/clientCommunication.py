import logging
from entryParsing.headerInterface import ClientHeader
import zmq
import os
from entryParsing.common.messageType import MessageType
from entryParsing.common.table import Table

MAX_TIMEOUTS = int(os.getenv('MAX_TIMEOUTS'))
class ClientCommunication:
    def __init__(self):
        self._context = zmq.Context()
        socketaddr = os.getenv('BORDER_NODE_ADDR') 
        id, socket  = ClientCommunication.manageHandshake(self._context, socketaddr)
        socket.setsockopt(zmq.IDENTITY, id)
        socket.setsockopt(zmq.RCVTIMEO, int(os.getenv('TIMEOUT')))
        socket.connect(socketaddr) 
        self._socket = socket
        self._responsesObtained = []

    def stop(self):
        self._socket.close()
    
    @staticmethod
    def manageHandshake(context, socketaddr):
        socket = context.socket(zmq.DEALER)
        socket.connect(socketaddr)
        socket.send(MessageType.CONNECT.serialize())
        handshakeResponse = socket.recv()
        msgType, idBytes = MessageType.deserialize(handshakeResponse)
        if msgType != MessageType.CONNECT_ACCEPT:
            raise Exception(f"Handshake failed: received {msgType}")
        socket.disconnect(socketaddr)
        return idBytes, socket
    
    def receiveFromServer(self):
        if self._responsesObtained:
            return self._responsesObtained.pop(0)
        try:
            msg = self._socket.recv()
            type, msg = MessageType.deserialize(msg)
            if not type == MessageType.QUERY_RESPONSE:
                raise Exception(f"Received message of type {type} when waiting for responses")
            return msg
            
        except zmq.error.Again:
            return None
    
    def sendDataToServer(self, msg):
        self._socket.send(MessageType.DATA_TRANSFER.serialize() + msg)

    def sendEndOfDataTransfer(self):
        msg = MessageType.FINISH_DATA_TRANSFER.serialize()
        self._socket.send(msg)
        retries = 0
        while retries < MAX_TIMEOUTS:
            try:
                if not self.waitForEndOfDataAck():
                    continue
                return
            except zmq.Again:
                self._socket.send(msg)
                retries += 1

    def waitForEndOfDataAck(self):
        msg = self._socket.recv()
        type, msg = MessageType.deserialize(msg)
        match type:
            case MessageType.ACK_END_OF_DATA:
                return True
            case MessageType.MESSAGE_ACK:
                # some repeated ack probably
                pass
            case MessageType.QUERY_RESPONSE:
                self._responsesObtained.append(msg)
            case _:
                raise Exception(f"Received a message of type {type} from server")
        return False
    
    def sendAllData(self, client, maxDataBytes, gamesGeneratorFunc, reviewsGeneratorFunc):
        self.sendTable(client, maxDataBytes, gamesGeneratorFunc, Table.GAMES)
        self.sendTable(client, maxDataBytes, reviewsGeneratorFunc, Table.REVIEWS)
        self.sendEndOfDataTransfer()

    def sendDataAndWaitForAck(self, fragment, eof, table, data):
        header = ClientHeader(fragment, eof, table)
        retries = 0
        self.sendDataToServer(header.serialize() + data)
        while retries < MAX_TIMEOUTS:
            try:
                if not self.waitForServerAck(header):
                    continue
                return
            except zmq.Again:
                self.sendDataToServer(header.serialize() + data)
                retries += 1

    def waitForServerAck(self, sentHeader: ClientHeader):
        msg = self._socket.recv()
        type, msg = MessageType.deserialize(msg)
        match type:
            case MessageType.MESSAGE_ACK:
                header, _ = ClientHeader.deserialize(msg)
                if header.isEqual(sentHeader):
                    return True
            case MessageType.QUERY_RESPONSE:
                self._responsesObtained.append(msg)
            case _:
                raise Exception(f"Received a message of type {type} from server")
        return False


    def sendTable(self, client, maxDataBytes, generatorFunction, table):
        # stop and wait logic, it sends one message at a time
        if not client.isRunning():
            return
        fragment = 1
        currPacket = bytes()
        generator = generatorFunction()
        logging.info(f'action: start sending table {table} | result: success')
        try:
            while client.isRunning():
                entry = next(generator)
                entryBytes = entry.serialize()
                if len(currPacket) + len(entryBytes) <= maxDataBytes:
                    currPacket += entryBytes
                else:
                    self.sendDataAndWaitForAck(fragment, False, table, currPacket)
                    fragment += 1
                    currPacket = entryBytes
        except StopIteration:
            self.sendDataAndWaitForAck(fragment, True, table, currPacket)
            logging.info(f'action: send table {table} end of file | result: success')