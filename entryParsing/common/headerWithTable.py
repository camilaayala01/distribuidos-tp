from entryParsing.common.table import Table
from .fieldParsing import TABLE_LEN, deserializeBoolean, deserializeCount, deserializeTable, serializeTable
from .header import Header

class HeaderWithTable(Header):
    def __init__(self, table: Table, fragment: int, eof: bool):
        self._table = table
        super().__init__(fragment, eof)

    def isGamesTable(self) -> bool:
        return Table.GAMES == self._table
    
    def isReviewsTable(self) -> bool:
        return Table.REVIEWS == self._table

    def serialize(self) -> bytes:
        return serializeTable(self._table) + super().serialize()
    
    def serializeWithoutTable(self) -> bytes:
        return super().serialize()
    
    @classmethod
    def size(cls):
        return super().size() + TABLE_LEN

    @staticmethod
    def deserialize(data: bytes) -> tuple['HeaderWithTable', bytes]:
        curr = 0
        try:
            table, curr = deserializeTable(curr, data)
            fragment, curr = deserializeCount(curr, data)
            eof, curr = deserializeBoolean(curr, data)
        except (IndexError, UnicodeDecodeError):
            raise Exception("There was an error parsing data in header")
        
        return HeaderWithTable(table, fragment, eof), data[curr:]