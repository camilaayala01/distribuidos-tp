import logging
import time
from entryParsing.common.clientHeader import ClientHeader
import zmq

from entryParsing.common.messageType import MessageType
from entryParsing.common.table import Table

MAX_TIMEOUTS = 10
TIMEOUT = 2000
class ClientCommunication:
    def __init__(self):
        self._context = zmq.Context()
        socketaddr = "tcp://border-node:%s" % "5556" # TODO: SACAR HARDCODEO
        id, socket  = ClientCommunication.manageHandshake(self._context, socketaddr)
        socket.setsockopt(zmq.IDENTITY, id)
        socket.setsockopt(zmq.RCVTIMEO, TIMEOUT) # TODO: SACAR HARDCODEO
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
        self._socket.send(MessageType.FINISH_DATA_TRANSFER.serialize())
        # wait for ack
    
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
                self.waitForServerAck(header)
            except:
                retries += 1
                time.sleep(1)


    # TODO add sending retries and maybe delete max timeouts
    def waitForServerAck(self, sentHeader: ClientHeader):
        timeoutCycles = 0
        while timeoutCycles < MAX_TIMEOUTS:
            try:
                msg = self._socket.recv()
                type, msg = MessageType.deserialize(msg)
                match type:
                    case MessageType.MESSAGE_ACK:
                        header, _ = ClientHeader.deserialize(msg)
                        if header.isEqual(sentHeader):
                            return
                    case MessageType.QUERY_RESPONSE:
                        self._responsesObtained.append(msg)
                    case _:
                        raise Exception(f"Received a message of type {type} from server")
            except zmq.Again:
                timeoutCycles += 1
                print("salto timeout")
        
        raise Exception(f"Couldn't send data correctly, server failed to ack message. tried:{timeoutCycles} times")

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