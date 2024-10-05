import math
from entryParsing.entry import EntryInterface

MAX_PACKET_SIZE = 4096

def boolToInt(boolean: bool) -> int:
    match boolean:
        case False:
            return 0
        case True:
            return 1
          
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

"""returns serialized data"""
def serializeAndFragmentWithSender(maxDataBytes: int, data: list[EntryInterface], id: int)-> list[bytes]: # recv max data bytes for testing purposes
    from .headerWithSender import HeaderWithSender
    fragment = 1
    packets = []
    currPacket = bytes()

    for entry in data:
        entryBytes = entry.serialize()
        if len(currPacket) + len(entryBytes) <= maxDataBytes:
            currPacket += entryBytes
        else:
            headerBytes = HeaderWithSender(id, fragment, False).serialize()
            fragment += 1
            packets.append(headerBytes + currPacket)
            currPacket = entryBytes

    packets.append(HeaderWithSender(id, fragment, True).serialize() + currPacket)
    return packets

# same as fragmenting with sender, but couldnt modularize
def serializeAndFragmentWithQueryNumber(maxDataBytes: int, data: list[EntryInterface], queryNumber: int)-> list[bytes]:
    from .headerWithQueryNumber import HeaderWithQueryNumber
    fragment = 1
    packets = []
    currPacket = bytes()

    for entry in data:
        entryBytes = entry.serialize()
        if len(currPacket) + len(entryBytes) <= maxDataBytes:
            currPacket += entryBytes
        else:
            headerBytes = HeaderWithQueryNumber(fragment, False, queryNumber).serialize()
            fragment += 1
            packets.append(headerBytes + currPacket)
            currPacket = entryBytes

    # will have to yield once we have memory restrictions
    packets.append(HeaderWithQueryNumber(fragment, True, queryNumber).serialize() + currPacket)
    return packets