from entryParsing.common.headerInterface import HeaderInterface
from entryParsing.common.fieldParsing import deserializeBoolean, deserializeCount, getClientID
class Header(HeaderInterface):
    def __init__(self, _clientId: bytes, _fragment: int, _eof: bool):
        super().__init__(_clientId=_clientId, _fragment=_fragment, _eof=_eof)
   
    @staticmethod
    def deserialize(data: bytes) -> tuple['Header', bytes]: 
        curr = 0
        try:
            clientId, curr = getClientID(curr, data)
            fragment, curr = deserializeCount(curr, data)
            eof, curr = deserializeBoolean(curr, data)
            header = Header(_clientId = clientId, _fragment = fragment, _eof = eof)
        except (IndexError, UnicodeDecodeError):
            raise Exception("There was an error parsing data in header")
        
        return header, data[curr:]