import math
from entryParsing.common.table import Table
from entryParsing.entry import EntryInterface
import time
MAX_PACKET_SIZE = 8192

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
        case "":
            return 0
        case _:
            print(string)
            raise(Exception("Boolean field could not be converted"))


def getShardingKey(id, nodeCount) -> int:
    return id % nodeCount

def maxDataBytes(headerType: type) -> int:
    return MAX_PACKET_SIZE - headerType.size()

def amountOfPacketsNeeded(headerType: type, byteCount: int) -> int:
    return math.ceil(byteCount / maxDataBytes(headerType))

"""returns serialized data"""
def serializeAndFragmentWithSender(maxDataBytes: int, data: list[EntryInterface], id: int)-> list[bytes]: # recv max data bytes for testing purposes
    from entryParsing.common.headerWithSender import HeaderWithSender
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
    from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
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

# same as fragmenting with sender, but couldnt modularize
def serializeAndFragmentWithTable(socket, maxDataBytes: int, generatorFunction, table: Table):
    from entryParsing.common.headerWithTable import HeaderWithTable
    fragment = 1
    currPacket = bytes()
    generator = generatorFunction()
    
    try:
        while True:
            entry = next(generator)
            entryBytes = entry.serialize()
            if len(currPacket) + len(entryBytes) <= maxDataBytes:
                currPacket += entryBytes
            else:
                headerBytes = HeaderWithTable(table, fragment, False).serialize()
                fragment += 1
                socket.send(headerBytes + currPacket)
                time.sleep(0.1)
                currPacket = entryBytes
    except StopIteration:
        print("sending eof")
        print(f' last fragment number is {fragment}')
        packet = HeaderWithTable(table, fragment, True).serialize() + currPacket
        socket.send(packet)