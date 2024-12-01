import csv
import logging
import os
import threading
import uuid
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.common.utils import nextRow
from eofController.eofControlMessage import EOFControlMessage, EOFControlMessageType
from internalCommunication.internalCommunication import InternalCommunication

class EofController:
    def __init__(self, nodeID, nodeName, nodeAmount, sendingStrategies):
        self._nodeID = nodeID
        self._nodeAmount = nodeAmount
        self._nodeName = nodeName
        self._internalCommunication = InternalCommunication(self._nodeName + 'EOF' + str(self._nodeID))
        self._pending = set()
        self._filepath = f"/{os.getenv('LISTENING_QUEUE')}/eofController"
        self.loadPendingFromDisk()
        self._sendingStrategies = sendingStrategies
        self._nextQueue = self._nodeName + 'EOF' + str((self._nodeID + 1) % self._nodeAmount)

    def loadPendingFromDisk(self):
        if os.path.isfile(self._filepath + '.tmp'):
            os.remove(self._filepath + '.tmp')

        if os.path.isfile(self._filepath + '.csv'):
            with open(self._filepath + '.csv', 'r') as file:
                reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
                while True:
                    row = nextRow(reader)
                    if row == None:
                        break
                    clientUUID = uuid.UUID(row[0]).bytes
                    self._pending.add(clientUUID)

    def storePendingInTemporaryFile(self, rename):
        with open(self._filepath + '.tmp', 'w+') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
            for client in self._pending:
                written = writer.writerow([f"{client}"]) # TODO: this probably needs a fix idk help
                if written < len(f"{client}"):
                    raise Exception('File could not be written propperly')   
        if rename:
            os.rename(self._filepath + '.tmp', self._filepath + '.csv') 


    def finishedProcessing(self, fragment, clientID, nodeInternalCommunication):
        self._pending.add(clientID)
        self.storePendingInTemporaryFile(False) 
        messageToSend = EOFControlMessage(EOFControlMessageType.EOF, clientID, self._nodeID, fragment).serialize()
        nodeInternalCommunication.basicSend(self._nextQueue, messageToSend) 
        os.rename(self._filepath + '.tmp', self._filepath + '.csv') 

    def terminateProcess(self, nodeInternalCommunication):
        messageToSend = EOFControlMessage(EOFControlMessageType.TERMINATION, 0, 0).serialize()
        nodeInternalCommunication.basicSend(self._nodeName + 'EOF' + str(self._nodeID), messageToSend)

    def manageEOF(self, clientID, fragment):
        eofMessage = HeaderWithSender(clientID, fragment, True, self._nodeID).serialize()
        for strategy in self._sendingStrategies:
            strategy.sendDataBytes(self._internalCommunication, eofMessage)
        logging.info(f'action: sending EOF for client {clientID}| result: success')
        messageToSend = EOFControlMessage(EOFControlMessageType.ACK, clientID, self._nodeID).serialize()
        self._internalCommunication.basicSend(self._nextQueue, messageToSend)

    def handleMessage(self, ch, method, _properties, body):
        msg = EOFControlMessage.deserialize(body)
        match msg.getType():
            case EOFControlMessageType.TERMINATION:
                ch.basic_ack(delivery_tag = method.delivery_tag)
                self.stop()
                return
            case EOFControlMessageType.ACK:
                if msg.getClientID() in self._pending:
                    self._pending.remove(msg.getClientID())
                    self.storePendingInTemporaryFile(True)
                if msg.getNodeID() != self._nodeID:
                    self._internalCommunication.basicSend(self._nextQueue, body)
            case EOFControlMessageType.EOF:
                if msg.getClientID() not in self._pending:
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                    return
                if msg.getNodeID() == self._nodeID:
                    self.manageEOF(msg.getClientID(), msg.getFragment())
                if msg.getNodeID() > self._nodeID:
                    self._internalCommunication.basicSend(self._nextQueue, body)
        
        ch.basic_ack(delivery_tag = method.delivery_tag)
        
    def stop(self):
        self._internalCommunication.stop()

    def execute(self):
        threading.Thread(target=self._internalCommunication.defineMessageHandler, args=(self.handleMessage,)).start()
