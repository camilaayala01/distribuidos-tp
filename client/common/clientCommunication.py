import logging
from entryParsing.common.clientHeader import ClientHeader
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
import zmq

class ClientCommunication:
    def __init__(self):
        context = zmq.Context()
        socket = context.socket(zmq.DEALER)
        socket.connect("tcp://border-node:%s" % "5556")
        self._socket = socket
        self._socket.setsockopt(zmq.RCVTIMEO, 100)

    def stop(self):
        self._socket.close()

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
                    headerBytes = ClientHeader(fragment, False, table).serialize()
                    fragment += 1
                    self.sendToServer(headerBytes + currPacket)
                    currPacket = entryBytes
        except StopIteration:
            packet = ClientHeader(fragment, True, table).serialize() + currPacket
            self.sendToServer(packet)
            logging.info(f'action: send table {table} end of file | result: success')