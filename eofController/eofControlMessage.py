from enum import Enum

from entryParsing.common.fieldParsing import deserializeNumber, getClientID, serializeNumber


class EOFControlMessageType(Enum):
    EOF = 0
    ACK = 1
    TERMINATION = 2

    def serialize(self):
        return serializeNumber(self.value, 1)

    @staticmethod
    def deserialize(data: bytes)-> tuple['EOFControlMessageType', bytes]:
        typeNumber, curr = deserializeNumber(0, data, 1)
        return EOFControlMessageType(typeNumber), curr

class EOFControlMessage:
    def __init__(self, type, clientID, nodeID):
        self._type = type
        self._clientID = clientID
        self._nodeID = nodeID

    def serialize(self) -> bytes:
        typeBytes = self._type.serialize()
        if self._type == EOFControlMessageType.TERMINATION:
            return typeBytes
        nodeIDBytes = serializeNumber(self._nodeID, 1)
        return typeBytes + self._clientID + nodeIDBytes
    
    def getClientID(self) -> bytes:
        return self._clientID
    
    def getType(self) -> EOFControlMessageType:
        return self._type

    def getNodeID(self) -> int:
        return self._nodeID

    @classmethod
    def deserialize(self, body) -> 'EOFControlMessage':
        type, curr = EOFControlMessageType.deserialize(body)
        if type == EOFControlMessageType.TERMINATION:
            return EOFControlMessage(type, bytes(1), 0)
        clientID, curr = getClientID(curr, body)
        nodeID, curr = deserializeNumber(curr, body, 1)
        return EOFControlMessage(type, clientID, nodeID)