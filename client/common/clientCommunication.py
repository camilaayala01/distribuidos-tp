import logging
from entryParsing.common.clientHeader import ClientHeader
import zmq

from entryParsing.common.messageType import MessageType
from entryParsing.common.table import Table

class ClientCommunication:
    def __init__(self):
        self._context = zmq.Context()
        socketaddr = "tcp://border-node:%s" % "5556" # TODO: SACAR HARDCODEO
        id, socket  = ClientCommunication.manageHandshake(self._context, socketaddr)
        socket.setsockopt(zmq.IDENTITY, id)
        socket.setsockopt(zmq.RCVTIMEO, 100) # TODO: SACAR HARDCODEO
        socket.connect(socketaddr) 
        self._socket = socket

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
        try:
            return self._socket.recv()
        except zmq.error.Again:
            return None
    
    def sendDataToServer(self, msg):
        self._socket.send(MessageType.DATA_TRANSFER.serialize() + msg)

    def sendEndOfDataTransfer(self):
        self._socket.send(MessageType.FINISH_DATA_TRANSFER.serialize())
        # wait for ack
    
    def sendAllData(self, client, maxDataBytes, gamesGeneratorFunc, reviewsGeneratorFunc):
        self.sendTable(client, maxDataBytes, gamesGeneratorFunc, Table.GAMES)
        self.sendTable(client, maxDataBytes, reviewsGeneratorFunc, Table.REVIEWS)
        self.sendEndOfDataTransfer()

    def sendDataAndWaitForAck(self, fragment, eof, table, data):
        headerBytes = ClientHeader(fragment, eof, table).serialize()
        self.sendDataToServer(headerBytes + data)
        # wait for ack

    def sendTable(self, client, maxDataBytes, generatorFunction, table):
        # add stop and wait logic, but change function so it sends one message at a time
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
                    # revise for ack
        except StopIteration:
            self.sendDataAndWaitForAck(fragment, True, table, currPacket)
            logging.info(f'action: send table {table} end of file | result: success')