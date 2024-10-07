from common.utils import storeResultsQuery1, storeResultsQuery2, storeResultsQuery3, storeResultsQuery4, storeResultsQuery5
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryName import EntryName
from entryParsing.entryNameAvgPlaytime import EntryNameAvgPlaytime
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from entryParsing.entryOSCount import EntryOSCount


def receiveQuery1Answer(data):
    response = EntryOSCount.deserialize(data)
    storeResultsQuery1("Total de juegos: " + str(response._total) + 
    "Total de juegos soportados en Windows: " + str(response._windows) + 
    "Total de juegos soportados en Linux: " + str(response._linux) +
    "Total de juegos soportados en Mac: " + str(response._mac))
    

def receiveCSVAnswer(data, includeHeader: bool, entryType, storageFunction):
    responses = entryType.deserialize(data)
    csvData = ""
    if includeHeader:
        csvData += entryType.header()
    for response in responses:
        csvData += response.csv()
    storageFunction(responses)

def receiveQuery2Answer(data, includeHeader: bool):
    receiveCSVAnswer(data, includeHeader, entryType=EntryNameAvgPlaytime, storageFunction=storeResultsQuery2)

def receiveQuery3Answer(data, includeHeader: bool):
    receiveCSVAnswer(data, includeHeader, entryType=EntryNameReviewCount, storageFunction=storeResultsQuery3)

def receiveQuery4Answer(data, includeHeader: bool):
    receiveCSVAnswer(data, includeHeader, entryType=EntryName, storageFunction=storeResultsQuery4)
    
def receiveQuery4Answer(data, includeHeader: bool):
    receiveCSVAnswer(data, includeHeader, entryType=EntryName, storageFunction=storeResultsQuery4)

def receiveQuery5Answer(data, includeHeader: bool):
    receiveCSVAnswer(data, includeHeader, entryType=EntryAppIDName, storageFunction=storeResultsQuery5)

def processResponse(data: bytes) -> bool:
    header, data = HeaderWithQueryNumber.deserialize(data)
    match header._queryNumber:
        case 1: receiveQuery1Answer(data)
        case 2: receiveQuery2Answer(data, header.getFragmentNumber() == 1)
        case 3: receiveQuery3Answer(data, header.getFragmentNumber() == 1)
        case 4: receiveQuery4Answer(data, header.getFragmentNumber() == 1)
        case 5: receiveQuery5Answer(data, header.getFragmentNumber() == 1)
        case default:
            raise(Exception("invalid query num"))
        
    return header._eof
