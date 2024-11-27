from enum import Enum

ID_LEN = 1
VALUE_LEN = 1

class ElectionMessage(Enum):
    ELECTION = 0
    ANSWER = 1
    COORDINATOR = 2

    def serialize(self, id: int) -> bytes:
        return int.to_bytes(int(self.value), VALUE_LEN, 'big') + int.to_bytes(id, ID_LEN, 'big')
    
    @classmethod
    def deserialize(cls, message) -> tuple['ElectionMessage', int]:
        return cls(value=int.from_bytes(message[:VALUE_LEN], 'big')), int.from_bytes(message[len(message) - ID_LEN:], 'big')
    