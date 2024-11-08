from entryParsing.common.fieldLen import BOOLEAN_LEN, COUNT_LEN, TABLE_LEN, MESSAGE_TYPE_LEN
from entryParsing.common.fieldParsing import serializeBoolean, serializeCount, serializeTable
from entryParsing.common.messageType import MessageType
from entryParsing.common.table import Table

class ClientHeader:
    def __init__(self, messageType: MessageType, fragment: int, eof: bool, table: Table):
        self._messageType = messageType
        self._fragment = fragment
        self._eof = eof
        self._table = table

    def getTable(self):
        return self._table

    def isGamesTable(self) -> bool:
        return Table.GAMES == self._table
    
    def isReviewsTable(self) -> bool:
        return Table.REVIEWS == self._table

    def size(self):
        return MESSAGE_TYPE_LEN + COUNT_LEN + BOOLEAN_LEN + TABLE_LEN
    
    def serialize(self) -> bytes:
        messageTypeBytes = MessageType.serialize(self._messageType)
        fragmentBytes = serializeCount(self._fragment)
        eofBytes = serializeBoolean(self._eof)
        tableBytes = serializeTable(self._table)
        return messageTypeBytes + fragmentBytes + eofBytes + tableBytes

    def __str__(self):
        return f"fragment: {self._fragment} | eof: {self._eof}"
    
    def getFragmentNumber(self) -> int:
        return self._fragment
    
    def isEOF(self) -> bool:
        return self._eof