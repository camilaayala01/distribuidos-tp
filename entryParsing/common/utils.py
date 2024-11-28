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

def nextRow(generator):
    try:
        row = next(generator)
        return row
    except StopIteration:
        return None
    
def convertFirstLetterToLowerCase(string: str):
    return string[0].lower() + string[1:]

def generateFullPath(path: str, module: str):
    return path + '.' + module

def getModuleFromEnvVars(entryType: str, path: str):
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
    return getModuleFromEnvVars(os.getenv('HEADER_TYPE'), 'HEADER_PATH')

def getEntryTypeFromEnv():
    return getModuleFromEnvVars(os.getenv('ENTRY_TYPE'), 'ENTRY_PATH')

def getGamesEntryTypeFromEnv():
    return getModuleFromEnvVars(os.getenv('GAMES_ENTRY_TYPE'), 'ENTRY_PATH')

def getReviewsEntryTypeFromEnv():
    return getModuleFromEnvVars(os.getenv('REVIEWS_ENTRY_TYPE'), 'ENTRY_PATH')

def getEntryTypeFromString(type: str):
    return getModuleFromEnvVars(type, 'ENTRY_PATH')

def getHeaderTypeFromString(type: str):
    return getModuleFromEnvVars(type, 'HEADER_PATH')

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

def copyFile(newResultsFile, oldFilePath):
    filepath = oldFilePath
    if not os.path.exists(filepath):
        return
    fileLen = os.stat(filepath).st_size
    with open(filepath, 'r+') as currentResults:
        copied = 0
        while copied < fileLen:
            copied += os.copy_file_range(currentResults.fileno(), newResultsFile.fileno(), fileLen)
