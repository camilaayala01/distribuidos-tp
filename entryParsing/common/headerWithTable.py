from entryParsing.common.table import Table
from entryParsing.common.fieldLen import TABLE_LEN
from entryParsing.common.fieldParsing import deserializeBoolean, deserializeCount, deserializeTable, getClientID, serializeTable
from entryParsing.common.header import Header

class HeaderWithTable(Header):
    def __init__(self, clientId: bytes, table: Table, fragment: int, eof: bool):
        super().__init__(clientId, fragment, eof)
        self._table = table

    def getTable(self):
        return self._table

    def isGamesTable(self) -> bool:
        return Table.GAMES == self._table
    
    def isReviewsTable(self) -> bool:
        return Table.REVIEWS == self._table

    def serialize(self) -> bytes:
        return super().serialize() + serializeTable(self._table)
    
    def serializeWithoutTable(self) -> bytes:
        return super().serialize()
    
    @classmethod
    def size(cls):
        return super().size() + TABLE_LEN
    
    def __str__(self):
        return f"fragment: {self._fragment} | eof: {self._eof} | table: {self._table}"
    
    @staticmethod
    def deserialize(data: bytes) -> tuple['HeaderWithTable', bytes]:
        curr = 0
        try:
            clientId, curr = getClientID(curr, data)
            fragment, curr = deserializeCount(curr, data)
            eof, curr = deserializeBoolean(curr, data)
            table, curr = deserializeTable(curr, data)
        except (IndexError, UnicodeDecodeError):
            raise Exception("There was an error parsing data in header")
        
        return HeaderWithTable(clientId, table, fragment, eof), data[curr:]