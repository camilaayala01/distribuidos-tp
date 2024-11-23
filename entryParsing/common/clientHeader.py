from entryParsing.common.fieldLen import BOOLEAN_LEN, COUNT_LEN, TABLE_LEN, MESSAGE_TYPE_LEN
from entryParsing.common.fieldParsing import deserializeBoolean, deserializeCount, deserializeTable, serializeBoolean, serializeCount, serializeTable
from entryParsing.common.table import Table

class ClientHeader:
    def __init__(self, fragment: int, eof: bool, table: Table):
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
    
    def isEqual(self, other: 'ClientHeader') -> bool:
        return self._fragment == other._fragment \
        and self._eof == other._eof \
        and self._table == other._table
    
    def isLastClientPacket(self) -> bool:
        return self._table == Table.REVIEWS and self._eof
    
    def serialize(self) -> bytes:
        fragmentBytes = serializeCount(self._fragment)
        eofBytes = serializeBoolean(self._eof)
        tableBytes = serializeTable(self._table)
        return fragmentBytes + eofBytes + tableBytes

    @staticmethod
    def deserialize(data: bytes) -> tuple['ClientHeader', bytes]:
        curr = 0
        try:
            fragment, curr = deserializeCount(curr, data)
            eof, curr = deserializeBoolean(curr, data)
            table, curr = deserializeTable(curr, data)
        except (IndexError, UnicodeDecodeError):
            raise Exception("There was an error parsing data in header")

        return ClientHeader(fragment, eof, table), data[curr:]

    def __str__(self):
        return f"fragment: {self._fragment} | eof: {self._eof}"
    
    def getFragmentNumber(self) -> int:
        return self._fragment
    
    def isEOF(self) -> bool:
        return self._eof