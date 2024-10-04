import math

from entryParsing.entry import EntryInterface

MAX_PACKET_SIZE = 4096

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

def maxDataBytes(headerType: type) -> int:
    return MAX_PACKET_SIZE - headerType.size()

def amountOfPacketsNeeded(headerType: type, byteCount: int) -> int:
    return math.ceil(byteCount / maxDataBytes(headerType))

def serializeAndFragment(self, headerType: type, maxDataBytes: int, data: EntryInterface)-> list[bytes]: # recv max data bytes for testing purposes
        fragment = 1
        packets = []
        currPacket = bytes()

        for entry in self._partialTop:
            entryBytes = entry.serialize()
            if len(currPacket) + len(entryBytes) <= maxDataBytes:
                currPacket += entryBytes
            else:
                headerBytes = headerType(self._id, fragment, False).serialize()
                fragment += 1
                packets.append(headerBytes + currPacket)
                currPacket = entryBytes

        packets.append(headerType(self._id, fragment, True).serialize() + currPacket)
        return packets