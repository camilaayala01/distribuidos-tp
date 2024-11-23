from enum import Enum
MESSAGE_TYPE_LEN = 1

class InternalMessageType(Enum):
    DATA_TRANSFER = 0 # sending info
    CLIENT_FLUSH = 1 # remove client from actives

    def serialize(self):
        return self.value.to_bytes(MESSAGE_TYPE_LEN,'big')

    @staticmethod
    def deserialize(data: bytes)-> tuple['InternalMessageType', bytes]:
        typeNumber = int.from_bytes(data[0:MESSAGE_TYPE_LEN], 'big')
        return InternalMessageType(typeNumber), data[MESSAGE_TYPE_LEN:]
