from typing import Tuple
from .table import Table
from .utils import boolToInt, intToBool

STRING_LEN = 1
COUNT_LEN = 4
AVG_PLAYTIME_LEN = 4
BOOLEAN_LEN = 1
TOP_BYTES_LEN = 1
SENDER_ID_LEN = 1
QUERY_NUMBER_LEN = 1
TABLE_LEN = 1
TEXT_LEN = 2

# 0 for games, 1 for reviews
def serializeTable(table: Table): 
    return table.value.to_bytes(TABLE_LEN,'big')

def deserializeTable(curr: int, data: bytes)-> Tuple[Table, int]:
    tableNum = int.from_bytes(data[curr:curr+TABLE_LEN], 'big')
    return Table(tableNum), curr + TABLE_LEN

def serializeVariableLenString(field: str):
    return serializeVariableLen(field, STRING_LEN)

def deserializeVariableLenString(curr: int, data: bytes)-> Tuple[str, int]:
    return deserializeVariableLen(curr, data, STRING_LEN)

def serializeReviewText(field: str):
    return serializeVariableLen(field, TEXT_LEN)

def deserializeReviewText(curr: int, data: bytes)-> Tuple[str, int]:
    return deserializeVariableLen(curr, data, TEXT_LEN)

def serializeVariableLen(field: str, fieldLen: int):
    fieldBytes = field.encode()
    fieldLenBytes = len(fieldBytes).to_bytes(fieldLen, 'big')
    return fieldLenBytes + fieldBytes

def deserializeVariableLen(curr: int, data: bytes, fieldLen: int)-> Tuple[str, int]:
    fieldLen = int.from_bytes(data[curr:curr+fieldLen], 'big')
    curr+=STRING_LEN
    appID = data[curr:fieldLen+curr].decode()
    return appID, curr + fieldLen

def serializeCount(count: int):
    return count.to_bytes(COUNT_LEN,'big')

def deserializeCount(curr: int, data: bytes)-> Tuple[int, int]:
    count = int.from_bytes(data[curr:curr+COUNT_LEN], 'big')
    return count, curr + COUNT_LEN

def serializeSenderID(senderID: int):
    return senderID.to_bytes(SENDER_ID_LEN,'big')

def deserializeSenderID(curr: int, data: bytes) -> Tuple[int, int]:
    senderID = int.from_bytes(data[curr:curr+SENDER_ID_LEN], 'big')
    return senderID, curr + SENDER_ID_LEN

def serializeBoolean(os: bool):
    return boolToInt(os).to_bytes(BOOLEAN_LEN,'big')

def deserializeBoolean(curr: int, data: bytes)-> Tuple[bool, int]:
    return intToBool(int.from_bytes(data[curr:curr+BOOLEAN_LEN], 'big')), curr + BOOLEAN_LEN

def serializePlaytime(avgPlaytime: int)-> Tuple[int, int]:
    return avgPlaytime.to_bytes(AVG_PLAYTIME_LEN,'big')

def deserializePlaytime(curr: int, data: bytes)-> Tuple[int, int]:
    avgPlaytime = int.from_bytes(data[curr:curr + AVG_PLAYTIME_LEN], 'big')
    return avgPlaytime, curr + AVG_PLAYTIME_LEN

def serializeTopCount(top: int):
    return top.to_bytes(TOP_BYTES_LEN,'big')

def deserializeTopCount(curr: int, data: bytes)-> Tuple[int, int]:
    top = int.from_bytes(data[curr:curr + TOP_BYTES_LEN], 'big')
    return top, curr + TOP_BYTES_LEN

def serializeQueryNumber(queryNumber: int):
    return queryNumber.to_bytes(QUERY_NUMBER_LEN,'big')

def deserializeQueryNumber(curr: int, data: bytes)-> Tuple[int, int]:
    top = int.from_bytes(data[curr:curr + QUERY_NUMBER_LEN], 'big')
    return top, curr + QUERY_NUMBER_LEN