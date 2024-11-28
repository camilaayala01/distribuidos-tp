from enum import Enum
MESSAGE_TYPE_LEN = 1

class InternalMessageType(Enum):
    SHUTDOWN = 0
    DATA_TRANSFER = 1 # sending info
    CLIENT_FLUSH = 2 # remove client from actives

    def serialize(self):
        return self.value.to_bytes(MESSAGE_TYPE_LEN,'big')

    @staticmethod
    def deserialize(data: bytes)-> tuple['InternalMessageType', bytes]:
        typeNumber = int.from_bytes(data[0:MESSAGE_TYPE_LEN], 'big')
        return InternalMessageType(typeNumber), data[MESSAGE_TYPE_LEN:]
