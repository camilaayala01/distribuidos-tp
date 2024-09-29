import random


def _boolToInt(boolean: bool) -> int:
    match boolean:
        case True:
            return 0
        case False:
            return 1  
def _intToBool(u8: int) -> bool:
    match u8:
        case 1:
            return False
        case 0:
            return True
        case _:
            raise Exception("There was an error parsing data")
        
def getRandomShardingKey(nodeCount):
    random.randint(0, nodeCount -1)

def getShardingKey(id, nodeCount):
    return hash(id) % nodeCount