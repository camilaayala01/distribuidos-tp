from enum import Enum
VALUE_LEN = 1

class HeartbeatMessage(Enum):
    CHECK = 0
    ACK = 1

    def serialize(self, id: str) -> bytes:
        return int.to_bytes(int(self.value), VALUE_LEN, 'big') + id.encode('utf-8')
    
    @classmethod
    def deserialize(cls, message) -> tuple['HeartbeatMessage', str]:
        return cls(int.from_bytes(message[:VALUE_LEN], 'big')), message[VALUE_LEN:].decode('utf-8')
    