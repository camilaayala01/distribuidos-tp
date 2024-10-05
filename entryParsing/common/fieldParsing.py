from .table import Table
from .utils import boolToInt, intToBool

COUNT_LEN = 3
AVG_PLAYTIME_LEN = 3
BOOLEAN_LEN = 1
TOP_BYTES_LEN = 1
SENDER_ID_LEN = 1
QUERY_NUMBER_LEN = 1
APP_ID_LEN = 1
NAME_LEN = 1
TABLE_LEN = 1
TEXT_LEN = 2
GENRE_LEN = 1
RELEASE_DATE_LEN = 10

# 0 for games, 1 for reviews
def serializeTable(table: Table): 
    return table.value.to_bytes(TABLE_LEN,'big')

def deserializeTable(curr: int, data: bytes)-> tuple[Table, int]:
    tableNum = int.from_bytes(data[curr:curr+TABLE_LEN], 'big')
    return Table(tableNum), curr + TABLE_LEN

def serializeGameName(field:str):
    return serializeVariableLen(field, NAME_LEN)

def deserializeGameName(curr: int, data: bytes)-> tuple[str, int]:
    return deserializeVariableLen(curr, data, NAME_LEN)

def serializeAppID(field: str):
    return serializeVariableLen(field, APP_ID_LEN)

def deserializeAppID(curr: int, data: bytes)-> tuple[str, int]:
    return deserializeVariableLen(curr, data, APP_ID_LEN)

def serializeReviewText(field: str):
    return serializeVariableLen(field, TEXT_LEN)

def deserializeReviewText(curr: int, data: bytes)-> tuple[str, int]:
    return deserializeVariableLen(curr, data, TEXT_LEN)

def serializeGenres(field: str):
    return serializeVariableLen(field, GENRE_LEN)

def deserializeGenres(curr: int, data: bytes)-> tuple[str, int]:
    return deserializeVariableLen(curr, data, GENRE_LEN)

def serializeVariableLen(field: str, fieldLen: int):
    fieldBytes = field.encode()
    fieldLenBytes = len(fieldBytes).to_bytes(fieldLen, 'big')
    return fieldLenBytes + fieldBytes

def deserializeVariableLen(curr: int, data: bytes, fieldLen: int)-> tuple[str, int]:
    field = int.from_bytes(data[curr:curr+fieldLen], 'big')
    curr+=fieldLen
    string = data[curr:field+curr].decode()
    return string, curr + field

def serializeReleaseDate(releaseDate: str):
    return releaseDate.encode()

def deserializeReleaseDate(curr: int, data: bytes) -> tuple[str]:
    return data[curr:curr+RELEASE_DATE_LEN].decode(), curr+RELEASE_DATE_LEN

def serializeCount(count: int):
    return count.to_bytes(COUNT_LEN,'big')

def deserializeCount(curr: int, data: bytes)-> tuple[int, int]:
    count = int.from_bytes(data[curr:curr+COUNT_LEN], 'big')
    return count, curr + COUNT_LEN

def serializeSenderID(senderID: int):
    return senderID.to_bytes(SENDER_ID_LEN,'big')

def deserializeSenderID(curr: int, data: bytes) -> tuple[int, int]:
    senderID = int.from_bytes(data[curr:curr+SENDER_ID_LEN], 'big')
    return senderID, curr + SENDER_ID_LEN

def serializeBoolean(os: bool):
    return boolToInt(os).to_bytes(BOOLEAN_LEN,'big')

def deserializeBoolean(curr: int, data: bytes)-> tuple[bool, int]:
    return intToBool(int.from_bytes(data[curr:curr+BOOLEAN_LEN], 'big')), curr + BOOLEAN_LEN

def serializePlaytime(avgPlaytime: int)-> tuple[int, int]:
    return avgPlaytime.to_bytes(AVG_PLAYTIME_LEN,'big')

def deserializePlaytime(curr: int, data: bytes)-> tuple[int, int]:
    avgPlaytime = int.from_bytes(data[curr:curr + AVG_PLAYTIME_LEN], 'big')
    return avgPlaytime, curr + AVG_PLAYTIME_LEN

def serializeTopCount(top: int):
    return top.to_bytes(TOP_BYTES_LEN,'big')

def deserializeTopCount(curr: int, data: bytes)-> tuple[int, int]:
    top = int.from_bytes(data[curr:curr + TOP_BYTES_LEN], 'big')
    return top, curr + TOP_BYTES_LEN

def serializeQueryNumber(queryNumber: int):
    return queryNumber.to_bytes(QUERY_NUMBER_LEN,'big')

def deserializeQueryNumber(curr: int, data: bytes)-> tuple[int, int]:
    top = int.from_bytes(data[curr:curr + QUERY_NUMBER_LEN], 'big')
    return top, curr + QUERY_NUMBER_LEN

def serializeNumber(number, size: int) -> bytes:
    return number.to_bytes(size,'big')

def deserializeNumber(data: bytes, curr: int, numberLen: int):
    number = int.from_bytes(data[curr:curr+numberLen], 'big')
    return number, curr + numberLen