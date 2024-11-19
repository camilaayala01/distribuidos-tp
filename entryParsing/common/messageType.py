from enum import Enum
from .fieldLen import MESSAGE_TYPE_LEN

class MessageType(Enum):
    CONNECT = 0 # client, for handshake
    CONNECT_ACCEPT = 1 # server, for successfull handshake
    CONNECT_RETRY = 2 # server, for when client is not registered correctly
    DATA_TRANSFER = 3 # client, for sending data after handshake
    FORMAT_ERROR = 4 # server, for telling client it sent an incorrect message
    MESSAGE_ACK = 5 # server, for telling client its message was received successfully
    QUERY_RESPONSE = 6 # server, for replying client with query data

    def serialize(self):
        return self.value.to_bytes(MESSAGE_TYPE_LEN,'big')

    @staticmethod
    def deserialize(data: bytes)-> tuple['MessageType', bytes]:
        typeNumber = int.from_bytes(data[0:MESSAGE_TYPE_LEN], 'big')
        return MessageType(typeNumber), data[MESSAGE_TYPE_LEN:]
