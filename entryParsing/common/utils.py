def boolToInt(boolean: bool) -> int:
    match boolean:
        case True:
            return 0
        case False:
            return 1
          
def intToBool(u8: int) -> bool:
    match u8:
        case 1:
            return False
        case 0:
            return True
        case _:
            raise Exception("There was an error parsing int to bool")

def getShardingKey(id, nodeCount) -> int:
    return hash(id) % nodeCount