from typing import Tuple
from .utils import boolToInt, intToBool

STRING_LEN = 1
COUNT_LEN = 4
BOOLEAN_BYTES = 1

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

def serializeBoolean(os: bool):
    return boolToInt(os).to_bytes(BOOLEAN_BYTES,'big')

def deserializeBoolean(curr: int, data: bytes)-> Tuple[bool, int]:
    return intToBool(int.from_bytes(data[curr:curr+BOOLEAN_BYTES], 'big')), curr + BOOLEAN_BYTES