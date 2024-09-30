from typing import Tuple
from .utils import boolToInt, intToBool

APP_ID_LEN = 1 
REVIEW_COUNT_LEN = 4
BOOLEAN_BYTES = 1

def serializeAppID(appId: str):
    appIDBytes = appId.encode()
    appIDLenByte = len(appIDBytes).to_bytes(APP_ID_LEN, 'big')
    return appIDLenByte + appIDBytes

def deserializeAppID(curr: int, data: bytes)-> Tuple[str, int]:
    appIDLen = int.from_bytes(data[curr:curr+APP_ID_LEN], 'big')
    curr+=APP_ID_LEN
    appID = data[curr:appIDLen+curr].decode()
    return appID, curr + appIDLen 

def serializeReviewCount(reviewCount: int):
    return reviewCount.to_bytes(REVIEW_COUNT_LEN,'big')

def deserializeReviewCount(curr: int, data: bytes)-> Tuple[str, int]:
    count = int.from_bytes(data[curr:curr+REVIEW_COUNT_LEN], 'big')
    return count, curr + REVIEW_COUNT_LEN

def serializeBoolean(os: bool):
    return boolToInt(os).to_bytes(BOOLEAN_BYTES,'big')

def deserializeBoolean(curr: int, data: bytes)-> Tuple[str, int]:
    return intToBool(int.from_bytes(data[curr:curr+BOOLEAN_BYTES], 'big')), curr + BOOLEAN_BYTES