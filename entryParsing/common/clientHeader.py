from entryParsing.common.fieldLen import BOOLEAN_LEN, COUNT_LEN, TABLE_LEN
from entryParsing.common.fieldParsing import deserializeBoolean, deserializeCount, serializeBoolean, serializeCount, serializeTable, deserializeTable
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
    
    def serializeWithoutTable(self) -> bytes:
        fragmentBytes = serializeCount(self._fragment)
        eofBytes = serializeBoolean(self._eof)
        return fragmentBytes + eofBytes

    def size(self):
        return COUNT_LEN + BOOLEAN_LEN + TABLE_LEN
    
    def serialize(self) -> bytes:
        return self.serializeWithoutTable() + serializeTable(self._table)

    def __str__(self):
        return f"fragment: {self._fragment} | eof: {self._eof}"
    
    def getFragmentNumber(self) -> int:
        return self._fragment
    
    def isEOF(self) -> bool:
        return self._eof

    @staticmethod
    def deserialize(data: bytes) -> tuple['ClientHeader', bytes]: 
        curr = 0
        try:
            fragment, curr = deserializeCount(curr, data)
            eof, curr = deserializeBoolean(curr, data)
            table, curr = deserializeTable(curr, data)
            header = ClientHeader(fragment, eof, table)
        except (IndexError, UnicodeDecodeError):
            raise Exception("There was an error parsing data in header")
        
        return header, data[curr:]