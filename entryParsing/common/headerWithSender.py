from entryParsing.common.fieldParsing import deserializeBoolean, deserializeCount, deserializeSenderID, serializeSenderID, getClientID
from entryParsing.common.fieldLen import SENDER_ID_LEN
from entryParsing.common.header import Header

class HeaderWithSender(Header):
    def __init__(self, clientId: bytes, fragment: int, eof: bool, senderID: int):
        super().__init__(clientId, fragment, eof)
        self._sender = senderID

    def serialize(self) -> bytes:
        return super().serialize() + serializeSenderID(self._sender)
    
    @classmethod
    def size(cls):
        return SENDER_ID_LEN + super().size()

    def __str__(self):
        return f"fragment: {self._fragment} | eof: {self._eof} | sender: {self._sender}"
    
    def getSenderID(self) -> int:
        return self._sender
    
    @staticmethod
    def deserialize(data: bytes) -> tuple['HeaderWithSender', bytes]:
        curr = 0
        try:
            clientId, curr = getClientID(curr, data)
            fragment, curr = deserializeCount(curr, data)
            eof, curr = deserializeBoolean(curr, data)
            senderId, curr = deserializeSenderID(curr, data)
        except (IndexError, UnicodeDecodeError):
            raise Exception("There was an error parsing data in header")
        
        return HeaderWithSender(clientId,  fragment, eof, senderId), data[curr:]