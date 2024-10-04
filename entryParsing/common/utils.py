import math

MAX_PACKET_SIZE = 4096

def boolToInt(boolean: bool) -> int:
    match boolean:
        case True:
            return 1
        case False:
            return 0
          
def intToBool(u8: int) -> bool:
    match u8:
        case 0:
            return False
        case 1:
            return True
        case _:
            raise Exception("There was an error parsing int to bool")

def strToBoolInt(string: str) -> int:
    match string: 
        case "True":
            return 1
        case "False":
            return 0
        case _:
            raise(Exception("Boolean field could not be converted"))


def getShardingKey(id, nodeCount) -> int:
    return hash(id) % nodeCount

def maxDataBytes(headerType: type) -> int:
    return MAX_PACKET_SIZE - headerType.size()

def amountOfPacketsNeeded(headerType: type, byteCount: int) -> int:
    return math.ceil(byteCount / maxDataBytes(headerType))