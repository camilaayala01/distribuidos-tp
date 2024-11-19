import threading
from entryParsing.common.fieldParsing import deserializeNumber, getClientID, serializeNumber
from internalCommunication.internalCommunication import InternalCommunication

class EOFControlMessage:
    def __init__(self, type, clientID, nodeID):
        self._type = type
        self._clientID = clientID
        self._nodeID = nodeID

    def serialize(self) -> bytes:
        typeBytes = serializeNumber(self._type, 1)
        nodeIDBytes = serializeNumber(self._nodeID, 2)
        return typeBytes + self._clientID + nodeIDBytes
    
    def getClientID(self) -> bytes:
        return self._clientID
    
    def isACK(self) -> bool:
        return True if self._type else False
    
    def getNodeID(self) -> int:
        return self._nodeID

    @classmethod
    def deserialize(self, body) -> 'EOFControlMessage':
        type, curr = deserializeNumber(0, body, 1)
        clientID, curr = getClientID(curr, body)
        nodeID, curr = deserializeNumber(curr, body, 2)
        return EOFControlMessage(type, clientID, nodeID)

class EofController:
    def __init__(self, nodeID, nodeName, nodeAmount, sendingStrategies):
        self._nodeID = nodeID
        self._nodeAmount = nodeAmount
        self._nodeName = nodeName
        self._internalCommunication = InternalCommunication(self._nodeName + 'EOF' + str(self._nodeID))
        self._eofMessage = {}
        self._sendingStrategies = sendingStrategies
        self._nextQueue = self._nodeName + 'EOF' + str((self._nodeID + 1) % self._nodeAmount)

    def finishedProcessing(self, eofMessage, clientID, nodeInternalCommunication):
        self._eofMessage[clientID] = eofMessage
        messageToSend = EOFControlMessage(0, clientID, self._nodeID).serialize()
        nodeInternalCommunication.basicSend(self._nextQueue, messageToSend)

    def manageEOF(self, clientID):
        curr = 0
        for strategy in self._sendingStrategies:
            strategy.sendBytes(self._internalCommunication, self._eofMessage[clientID][curr])
            curr += 1
        print('EOF WAS SENT')
        messageToSend = EOFControlMessage(1, clientID, self._nodeID).serialize()
        self._internalCommunication.basicSend(self._nextQueue, messageToSend)

    def handleMessage(self, ch, method, _properties, body):
        msg = EOFControlMessage.deserialize(body)
        if msg.isACK():
            del self._eofMessage[msg.getClientID()]
            ch.basic_ack(delivery_tag = method.delivery_tag)
            if msg.getNodeID() != self._nodeID:
                self._internalCommunication.basicSend(self._nextQueue, body)
            return
        if msg.getClientID() not in self._eofMessage:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return
        if msg.getNodeID() == self._nodeID:
            self.manageEOF(msg.getClientID())
        if msg.getNodeID() > self._nodeID:
            self._internalCommunication.basicSend(self._nextQueue, body)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def stop(self, _signum, _frame):
        self._internalCommunication.stop()

    def execute(self):
        threading.Thread(target=self._internalCommunication.defineMessageHandler, args=(self.handleMessage,)).start()
