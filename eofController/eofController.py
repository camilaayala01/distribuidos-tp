import threading
from internalCommunication.internalCommunication import InternalCommunication

class EofController:
    def __init__(self, nodeID, nodeName, nodeAmount, sendingStrategies):
        self._nodeID = nodeID
        self._nodeAmount = nodeAmount
        self._nodeName = nodeName
        self._internalCommunication = InternalCommunication(self._nodeName + 'EOF' + str(self._nodeID))
        self._eofMessage = {}
        self._sendingStrategies = sendingStrategies
        self._nextQueue = self._nodeName + 'EOF' + str(self._nodeID % self._nodeAmount) + 1

    def finishedProcessing(self, eofMessage, clientID):
        self._eofMessage[clientID] = eofMessage
        messageToSend = bytes(str(0) + str(clientID) + str(self._nodeID))
        self._internalCommunication.basicSend(self._nextQueue, messageToSend)

    def manageEOF(self, clientID):
        for strategy in self._sendingStrategies:
            strategy.sendBytes(self._internalCommunication, self._eofMessage)
        messageToSend = bytes(str(1) + str(clientID))
        self._internalCommunication.basicSend(self._nextQueue, messageToSend)

    def handleMessage(self, ch, method, _properties, body):
        messageType = int(body[0])
        clientID = int(body[1])
        if messageType:
            del self._eofMessage[clientID]
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
        if clientID not in self._eofMessage:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return
        nodeID = int(body[2])
        if nodeID == self._nodeID:
            self.manageEOF(clientID)
        if nodeID > self._nodeID:
            messageToSend = bytes(str(clientID) + str(nodeID))
            self._internalCommunication.basicSend(self._nextQueue, messageToSend)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def stop(self, _signum, _frame):
        self._internalCommunication.stop()

    def execute(self):
        threading.Thread(target=self._internalCommunication.defineMessageHandler(self.handleMessage)).start()
