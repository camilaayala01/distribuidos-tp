from .fieldParsing import SENDER_ID_LEN, deserializeBoolean, deserializeCount, deserializeSenderID, serializeSenderID
from .header import Header

class HeaderWithSender(Header):
    def __init__(self,  senderID: int, fragment: int, eof: bool):
        self._sender = senderID
        super().__init__(fragment, eof)

    def serialize(self) -> bytes:
        return serializeSenderID(self._sender) + super().serialize()
    
    @classmethod
    def size(cls):
        return SENDER_ID_LEN + super().size()

    @staticmethod
    def deserialize(data: bytes) -> tuple['Header', bytes]:
        curr = 0
        try:
            senderId, curr = deserializeSenderID(curr, data)
            fragment, curr = deserializeCount(curr, data)
            eof, curr = deserializeBoolean(curr, data)
        except (IndexError, UnicodeDecodeError):
            raise Exception("There was an error parsing data in header")
        
        return HeaderWithSender(senderId, fragment, eof), data[curr:]