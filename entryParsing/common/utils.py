import os
import importlib
import math
import logging
from entryParsing.entry import EntryInterface
import hashlib

MAX_PACKET_SIZE = 8192

def initializeLog():
    """
    Python custom logging initialization

    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    logging.getLogger("pika").setLevel(logging.WARNING)

def convertFirstLetterToLowerCase(string: str):
    return string[0].lower() + string[1:]

def generateFullPath(path: str, module: str):
    return path + '.' + module

def getModuleFromEnvVars(type: str, path: str):
    entryType = os.getenv(type)
    if not entryType:
        raise ValueError("Type environment variable is missing.")
    entryPath = os.getenv(path)
    if not entryPath:
        raise ValueError("Path environment variable is missing.")
    
    try:
        classImport = generateFullPath(entryPath, convertFirstLetterToLowerCase(entryType)) + '.' + entryType
        moduleName, classImport = classImport.rsplit('.', 1)
        module = importlib.import_module(moduleName)
        return getattr(module, classImport)
    except Exception as e:
        raise ImportError(f"Class '{classImport}' could not be found in module '{moduleName}'.")

def getHeaderTypeFromEnv():
    return getModuleFromEnvVars('HEADER_TYPE', 'HEADER_PATH')

def getEntryTypeFromEnv():
    return getModuleFromEnvVars('ENTRY_TYPE', 'ENTRY_PATH')

def getGamesEntryTypeFromEnv():
    return getModuleFromEnvVars('GAMES_ENTRY_TYPE', 'ENTRY_PATH')

def getReviewsEntryTypeFromEnv():
    return getModuleFromEnvVars('REVIEWS_ENTRY_TYPE', 'ENTRY_PATH')

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
            raise(Exception("Boolean field could not be converted"))


def getShardingKey(id: str, nodeCount: int) -> int:
    return int(hashlib.sha256(id.encode()).hexdigest(), 16) % nodeCount

def maxDataBytes(headerType: type) -> int:
    return MAX_PACKET_SIZE - headerType.size()

def amountOfPacketsNeeded(headerType: type, byteCount: int) -> int:
    return math.ceil(byteCount / maxDataBytes(headerType))

def serializeAndFragmentWithSender(maxDataBytes: int, data: list[EntryInterface], id: int, fragment: int = 1, hasEOF: bool = True)-> tuple[list[bytes], int]: # recv max data bytes for testing purposes
    from entryParsing.common.headerWithSender import HeaderWithSender
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

    packets.append(HeaderWithSender(id, fragment, hasEOF).serialize() + currPacket)
    fragment += 1
    return packets, fragment


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
