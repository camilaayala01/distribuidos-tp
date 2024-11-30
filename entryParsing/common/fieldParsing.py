import datetime
import struct
import uuid
from entryParsing.common.table import Table
from entryParsing.common.utils import boolToInt, intToBool
from entryParsing.common import fieldLen

MAX_REVIEW_TEXT = 150

def floatToInt(number) -> int:
    return int(number * 100)
        
def tryToFloat(string)-> float:
    try: 
        return float(string)
    except Exception:
        return 0
    
def parseDate(string)-> datetime.datetime:
    try:
        return datetime.datetime.strptime(string,"%b %d, %Y").strftime("%d-%m-%Y")
    except Exception:
        return datetime.datetime.strptime("1 " + string, "%d %b %Y").strftime("%d-%m-%Y")

# 0 for games, 1 for reviews
def serializeTable(table: Table): 
    return table.value.to_bytes(fieldLen.TABLE_LEN,'big')

def deserializeTable(curr: int, data: bytes)-> tuple[Table, int]:
    tableNum = int.from_bytes(data[curr:curr+fieldLen.TABLE_LEN], 'big')
    table = Table(tableNum)
    return table, curr + fieldLen.TABLE_LEN

def serializeGameName(field:str):
    return serializeVariableLen(field, fieldLen.NAME_LEN)

def deserializeGameName(curr: int, data: bytes)-> tuple[str, int]:
    return deserializeVariableLen(curr, data, fieldLen.NAME_LEN)

def serializeAppID(field: str):
    return serializeVariableLen(field, fieldLen.APP_ID_LEN)

def deserializeAppID(curr: int, data: bytes)-> tuple[str, int]:
    return deserializeVariableLen(curr, data, fieldLen.APP_ID_LEN)

def serializeReviewText(field: str):
    return serializeVariableLen(field, fieldLen.TEXT_LEN)

def skipReviewText(curr: int, data: bytes)-> int:
    return skipVariableLen(curr, data, fieldLen.TEXT_LEN)

def deserializeReviewText(curr: int, data: bytes)-> tuple[str, int]:
    text, curr = deserializeVariableLen(curr, data, fieldLen.TEXT_LEN)
    return text[:MAX_REVIEW_TEXT]

def serializeGenres(field: str):
    return serializeVariableLen(field, fieldLen.GENRE_LEN)

def deserializeGenres(curr: int, data: bytes)-> tuple[str, int]:
    return deserializeVariableLen(curr, data, fieldLen.GENRE_LEN)

def serializeVariableLen(field: str, fieldLen: int):
    fieldBytes = field.encode()
    fieldLenBytes = len(fieldBytes).to_bytes(fieldLen, 'big')
    return fieldLenBytes + fieldBytes

def skipVariableLen(curr: int, data: bytes, fieldLen: int)-> int:
    field = int.from_bytes(data[curr:curr+fieldLen], 'big')
    return curr + field + fieldLen

def deserializeVariableLen(curr: int, data: bytes, fieldLen: int)-> tuple[str, int]:
    field = int.from_bytes(data[curr:curr+fieldLen], 'big')
    curr+=fieldLen
    string = data[curr:field+curr].decode()
    return string, curr + field

def serializeReleaseDate(releaseDate: str):
    return releaseDate.encode()

def deserializeReleaseDate(curr: int, data: bytes) -> tuple[str]:
    return data[curr:curr+fieldLen.RELEASE_DATE_LEN].decode(), curr+fieldLen.RELEASE_DATE_LEN

def serializeCount(count: int):
    return count.to_bytes(fieldLen.COUNT_LEN,'big')

def deserializeCount(curr: int, data: bytes)-> tuple[int, int]:
    count = int.from_bytes(data[curr:curr+fieldLen.COUNT_LEN], 'big')
    return count, curr + fieldLen.COUNT_LEN

def serializeSenderID(senderID: int):
    return senderID.to_bytes(fieldLen.SENDER_ID_LEN,'big')

def deserializeSenderID(curr: int, data: bytes) -> tuple[int, int]:
    senderID = int.from_bytes(data[curr:curr+fieldLen.SENDER_ID_LEN], 'big')
    return senderID, curr + fieldLen.SENDER_ID_LEN

def serializeBoolean(os: bool) -> bytes:
    return boolToInt(os).to_bytes(fieldLen.BOOLEAN_LEN,'big')

def deserializeBoolean(curr: int, data: bytes)-> tuple[bool, int]:
    return intToBool(int.from_bytes(data[curr:curr+fieldLen.BOOLEAN_LEN], 'big')), curr + fieldLen.BOOLEAN_LEN

def serializePlaytime(avgPlaytime: int)-> tuple[int, int]:
    return avgPlaytime.to_bytes(fieldLen.AVG_PLAYTIME_LEN,'big')

def skipPlaytime(curr: int)-> int:
    return curr + fieldLen.AVG_PLAYTIME_LEN

def deserializePlaytime(curr: int, data: bytes)-> tuple[int, int]:
    avgPlaytime = int.from_bytes(data[curr:curr + fieldLen.AVG_PLAYTIME_LEN], 'big')
    return avgPlaytime, curr + fieldLen.AVG_PLAYTIME_LEN

def serializeQueryNumber(queryNumber: int):
    return queryNumber.to_bytes(fieldLen.QUERY_NUMBER_LEN,'big')

def deserializeQueryNumber(curr: int, data: bytes)-> tuple[int, int]:
    top = int.from_bytes(data[curr:curr + fieldLen.QUERY_NUMBER_LEN], 'big')
    return top, curr + fieldLen.QUERY_NUMBER_LEN

def serializeNumber(number, size: int) -> bytes:
    return number.to_bytes(size,'big')

def deserializeNumber(curr: int, data: bytes, numberLen: int):
    number = int.from_bytes(data[curr:curr+numberLen], 'big')
    return number, curr + numberLen

def serializeSignedInt(number: int):
    return struct.pack('b', number)

def deserializeSignedInt(curr: int, data: bytes) -> int:
    return struct.unpack('b', data[curr:curr+1])[0], curr + 1

def getClientID(curr: int, data: bytes) -> tuple[bytes, int]:
    return data[curr:curr + fieldLen.CLIENT_ID_LEN], curr + fieldLen.CLIENT_ID_LEN

def getClientIdUUID(clientId: bytes):
    return uuid.UUID(bytes=clientId)