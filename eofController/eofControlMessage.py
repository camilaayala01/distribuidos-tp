from enum import Enum
from entryParsing.common.fieldParsing import deserializeCount, deserializeNumber, getClientID, serializeCount, serializeNumber

CONTROL_LEN = 1
class EOFControlMessageType(Enum):
    EOF = 0
    ACK = 1
    TERMINATION = 2

    def serialize(self):
        return serializeNumber(self.value, CONTROL_LEN)

    @staticmethod
    def deserialize(data: bytes)-> tuple['EOFControlMessageType', bytes]:
        typeNumber, curr = deserializeNumber(0, data, CONTROL_LEN)
        return EOFControlMessageType(typeNumber), curr

class EOFControlMessage:
    def __init__(self, type, clientID, nodeID, fragment=0):
        self._type = type
        self._clientID = clientID
        self._nodeID = nodeID
        self._fragment = fragment

    def serialize(self) -> bytes:
        typeBytes = self._type.serialize()
        if self._type == EOFControlMessageType.TERMINATION:
            return typeBytes
        nodeIDBytes = serializeNumber(self._nodeID, 1)
        fragmentBytes = serializeCount(self._fragment)
        return typeBytes + self._clientID + nodeIDBytes + fragmentBytes
    
    def getClientID(self) -> bytes:
        return self._clientID
    
    def getType(self) -> EOFControlMessageType:
        return self._type

    def getNodeID(self) -> int:
        return self._nodeID

    def getFragment(self) -> int:
        return self._fragment

    def __repr__(self):
        return f"type: {self._type} client id: {self._clientID} node id: {self._nodeID}"
    
    @classmethod
    def deserialize(self, body) -> 'EOFControlMessage':
        type, curr = EOFControlMessageType.deserialize(body)
        if type == EOFControlMessageType.TERMINATION:
            return EOFControlMessage(type, bytes(1), 0)
        clientID, curr = getClientID(curr, body)
        nodeID, curr = deserializeNumber(curr, body, 1)
        fragment, curr = deserializeCount(curr, body)
        return EOFControlMessage(type, clientID, nodeID, fragment)