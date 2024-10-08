from common.utils import storeResultsQuery1, storeResultsQuery2, storeResultsQuery3, storeResultsQuery4, storeResultsQuery5
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryName import EntryName
from entryParsing.entryNameAvgPlaytime import EntryNameAvgPlaytime
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from entryParsing.entryOSCount import EntryOSCount
import logging

def receiveQuery1Answer(data):
    response = EntryOSCount.deserialize(data)
    logging.info(f'action: store query 1 data | data received: {response}')
    storeResultsQuery1(str(response))
    
def receiveCSVAnswer(data, includeHeader: bool, entryType, storageFunction, queryNum):
    responses = entryType.deserialize(data)
    csvData = ""
    loggingData = ""
    if includeHeader:
        csvData += entryType.header()
    for response in responses:
        csvData += response.csv()
        loggingData += str(response)
    logging.info(f'action: store query {queryNum} data | data received: {loggingData}')
    storageFunction(csvData)

def receiveQuery2Answer(data, includeHeader: bool):
    receiveCSVAnswer(data, includeHeader, entryType=EntryNameAvgPlaytime, storageFunction=storeResultsQuery2, queryNum=2)

def receiveQuery3Answer(data, includeHeader: bool):
    receiveCSVAnswer(data, includeHeader, entryType=EntryNameReviewCount, storageFunction=storeResultsQuery3, queryNum=3)

def receiveQuery4Answer(data, includeHeader: bool):
    receiveCSVAnswer(data, includeHeader, entryType=EntryName, storageFunction=storeResultsQuery4, queryNum = 4)
    
def receiveQuery5Answer(data, includeHeader: bool):
    receiveCSVAnswer(data, includeHeader, entryType=EntryAppIDName, storageFunction=storeResultsQuery5, queryNum=5)

def processResponse(data: bytes) -> bool:
    header, data = HeaderWithQueryNumber.deserialize(data)
    logging.info(f'action: receive response for query {header.getQueryNumber()} | {header} | result: success ')
    match header.getQueryNumber():
        case 1: receiveQuery1Answer(data)
        case 2: receiveQuery2Answer(data, header.getFragmentNumber() == 1)
        case 3: receiveQuery3Answer(data, header.getFragmentNumber() == 1)
        case 4: receiveQuery4Answer(data, header.getFragmentNumber() == 1)
        case 5: receiveQuery5Answer(data, header.getFragmentNumber() == 1)
        case default:
            raise(Exception("invalid query num"))
        
    return header.isEOF()
