from typing import Tuple
from .utils import boolToInt, intToBool

STRING_LEN = 1
COUNT_LEN = 4
AVG_PLAYTIME_LEN = 4
BOOLEAN_BYTES = 1
TOP_BYTES_LEN = 1
SENDER_ID_LEN = 1

def serializeVariableLenString(field: str):
    fieldBytes = field.encode()
    fieldLenBytes = len(fieldBytes).to_bytes(STRING_LEN, 'big')
    return fieldLenBytes + fieldBytes

def deserializeVariableLenString(curr: int, data: bytes)-> Tuple[str, int]:
    fieldLen = int.from_bytes(data[curr:curr+STRING_LEN], 'big')
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
    return boolToInt(os).to_bytes(BOOLEAN_BYTES,'big')

def deserializeBoolean(curr: int, data: bytes)-> Tuple[bool, int]:
    return intToBool(int.from_bytes(data[curr:curr+BOOLEAN_BYTES], 'big')), curr + BOOLEAN_BYTES

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