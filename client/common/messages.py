from common.utils import storeResultsQuery1, storeResultsQuery, storeHeader
from entryParsing.common.clientHeader import ClientHeader
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryName import EntryName
from entryParsing.entryNameAvgPlaytime import EntryNameAvgPlaytime
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from entryParsing.entryOSCount import EntryOSCount
import logging
from common.client import Client
from time import sleep
from entryParsing.common.table import Table
from entryParsing.common.headerWithTable import HeaderWithTable

def receiveQuery1Answer(data):
    response = EntryOSCount.deserialize(data)
    logging.info(f'action: store query 1 data | data received: {response}')
    storeResultsQuery1(str(response))
    
def receiveCSVAnswer(data, includeHeader: bool, entryType, queryNum):
    if includeHeader:
        storeHeader(entryType.header(), f'/query{queryNum}.csv')
    responses = entryType.deserialize(data)
    csvData, loggingData = "", ""
    for response in responses:
        csvData += response.csv()
        loggingData += str(response)
    logging.info(f'action: store query {queryNum} data | data received: {loggingData}')
    storeResultsQuery(csvData, f'/query{queryNum}.csv')

def receiveQuery2Answer(data, includeHeader: bool):
    receiveCSVAnswer(data, includeHeader, entryType=EntryNameAvgPlaytime, queryNum=2)

def receiveQuery3Answer(data, includeHeader: bool):
    receiveCSVAnswer(data, includeHeader, entryType=EntryNameReviewCount, queryNum=3)

def receiveQuery4Answer(data, includeHeader: bool):
    receiveCSVAnswer(data, includeHeader, entryType=EntryName, queryNum = 4)
    
def receiveQuery5Answer(data, includeHeader: bool):
    receiveCSVAnswer(data, includeHeader, entryType=EntryAppIDName, queryNum=5)

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


# same as fragmenting with sender, but couldnt modularize
def serializeAndFragmentWithTable(client: Client, maxDataBytes: int, generatorFunction, table: Table):
    if not client.isRunning():
        return
    fragment = 1
    currPacket = bytes()
    generator = generatorFunction()
    logging.info(f'action: start sending table {table} | result: success')
    try:
        while client.isRunning():
            entry = next(generator)
            entryBytes = entry.serialize()
            if len(currPacket) + len(entryBytes) <= maxDataBytes:
                currPacket += entryBytes
            else:
                headerBytes = ClientHeader(fragment, False, table).serialize()
                fragment += 1
                client.sendToServer(headerBytes + currPacket)
                currPacket = entryBytes
    except StopIteration:
        packet = ClientHeader(fragment, True, table).serialize() + currPacket
        client.sendToServer(packet)
        logging.info(f'action: send table {table} end of file | result: success')