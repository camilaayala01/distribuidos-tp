import logging
from entryParsing.common.clientHeader import ClientHeader
import zmq

from entryParsing.common.messageType import MessageType

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
        idBytes = socket.recv()
        socket.disconnect(socketaddr)
        return idBytes, socket
    
    def receiveFromServer(self):
        try:
            return self._socket.recv()
        except zmq.error.Again:
            return None
    
    def sendToServer(self, msg):
        self._socket.send(msg)

    def sendTable(self, client, maxDataBytes, generatorFunction, table):
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
                    headerBytes = ClientHeader(MessageType.DATA_TRANSFER, fragment, False, table).serialize()
                    fragment += 1
                    self.sendToServer(headerBytes + currPacket)
                    currPacket = entryBytes
        except StopIteration:
            packet = ClientHeader(MessageType.DATA_TRANSFER, fragment, True, table).serialize() + currPacket
            self.sendToServer(packet)
            logging.info(f'action: send table {table} end of file | result: success')