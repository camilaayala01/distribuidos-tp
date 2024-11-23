from enum import Enum
from .fieldLen import MESSAGE_TYPE_LEN

class MessageType(Enum):
    # client, for handshake
    CONNECT = 0 
    # server, for successfull handshake
    CONNECT_ACCEPT = 1 
    # server, for when client is not registered correctly
    CONNECT_RETRY = 2 
    # client, for sending data after handshake
    DATA_TRANSFER = 3
    # server, for telling client it sent an incorrect message 
    FORMAT_ERROR = 4 
    # server, for telling client its message was received successfully
    MESSAGE_ACK = 5 
    # server, for replying client with query data
    QUERY_RESPONSE = 6 
    # client, for announcing to server they wont send more data. this is used for client
    # to ensure server wont think it got disconnected
    FINISH_DATA_TRANSFER = 7 

    def serialize(self):
        return self.value.to_bytes(MESSAGE_TYPE_LEN,'big')

    @staticmethod
    def deserialize(data: bytes)-> tuple['MessageType', bytes]:
        typeNumber = int.from_bytes(data[0:MESSAGE_TYPE_LEN], 'big')
        return MessageType(typeNumber), data[MESSAGE_TYPE_LEN:]
