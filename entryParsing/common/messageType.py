from enum import Enum
from .fieldLen import MESSAGE_TYPE_LEN
class MessageType(Enum):
    CONNECT = 0
    DATA_TRANSFER = 1

    def serialize(self):
        return self.value.to_bytes(MESSAGE_TYPE_LEN,'big')

    @staticmethod
    def deserialize(data: bytes)-> tuple['MessageType', bytes]:
        typeNumber = int.from_bytes(data[0:MESSAGE_TYPE_LEN], 'big')
        return MessageType(typeNumber), data[MESSAGE_TYPE_LEN:]
