from .common.table import Table
from .common import fieldLen
from .messagePart import MessagePartInterface

class HeaderInterface(MessagePartInterface):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self):
        return f"client: {self._clientId} | fragment: {self._fragment} | eof: {self._eof}"
    
    def getClient(self) -> int:
        return self._clientId

    def getFragmentNumber(self) -> int:
        return self._fragment
    
    def isEOF(self) -> bool:
        return self._eof
    
    def getTable(self):
        return self._table

    def isGamesTable(self) -> bool:
        return Table.GAMES == self._table
    
    def isReviewsTable(self) -> bool:
        return Table.REVIEWS == self._table
    
    def getSenderID(self) -> int:
        return self._sender
    
    def getQueryNumber(self):
        return self._queryNumber
    
    @classmethod
    def deserialize(cls, data: bytes): 
        header, curr = cls.deserializeEntry(0, data)
        return header, data[curr:]
    
    @classmethod
    def size(cls):
        return fieldLen.COUNT_LEN + fieldLen.BOOLEAN_LEN + fieldLen.CLIENT_ID_LEN


class Header(HeaderInterface):
    def __init__(self, _clientId: bytes, _fragment: int, _eof: bool):
        super().__init__(_clientId=_clientId, _fragment=_fragment, _eof=_eof)


class HeaderWithQueryNumber(HeaderInterface):
    def __init__(self, _clientId: bytes, _fragment: int, _eof: bool, _queryNumber: int):
        super().__init__(_clientId=_clientId, _fragment=_fragment, _eof=_eof, _queryNumber=_queryNumber)

    def __str__(self):
        return f"fragment: {self._fragment} | eof: {self._eof} | query number: {self._queryNumber}"
    
    @classmethod
    def size(cls):
        return super().size() + fieldLen.QUERY_NUMBER_LEN
    

class HeaderWithTable(HeaderInterface):
    def __init__(self, _clientId: bytes, _fragment: int, _eof: bool, _table: Table):
        super().__init__(_clientId=_clientId, _fragment=_fragment, _eof=_eof, _table=_table)
    
    def __str__(self):
        return f" clientId: {self._clientId} | fragment: {self._fragment} | eof: {self._eof} | table: {self._table}"
    
    @classmethod
    def size(cls):
        return super().size() + fieldLen.TABLE_LEN
    

class HeaderWithSender(HeaderInterface):
    def __init__(self, _clientId: bytes, _fragment: int, _eof: bool, _sender: int):
        super().__init__(_clientId=_clientId, _fragment=_fragment, _eof=_eof, _sender =_sender)

    def __str__(self):
        return f"fragment: {self._fragment} | eof: {self._eof} | sender: {self._sender}"
    
    @classmethod
    def size(cls):
        return super().size() + fieldLen.SENDER_ID_LEN

class ClientHeader(HeaderInterface):
    def __init__(self, _fragment: int, _eof: bool, _table: Table):
        super().__init__(_fragment=_fragment, _eof=_eof, _table=_table)
    
    def isEqual(self, other: 'ClientHeader') -> bool:
        return self._fragment == other._fragment \
        and self._eof == other._eof \
        and self._table == other._table
    
    def size(self):
        return fieldLen.MESSAGE_TYPE_LEN + fieldLen.COUNT_LEN + fieldLen.BOOLEAN_LEN + fieldLen.TABLE_LEN

    def isLastClientPacket(self) -> bool:
        return self._table == Table.REVIEWS and self._eof

    def __str__(self):
        return f"fragment: {self._fragment} | eof: {self._eof}"