import logging
import os
from common.utils import receiveCSVAnswer, storeResultsQuery1
from common.clientCommunication import ClientCommunication
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.entryAppIDName import EntryAppIDName
from entryParsing.entryName import EntryName
from entryParsing.entryNameAvgPlaytime import EntryNameAvgPlaytime
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from entryParsing.entryOSCount import EntryOSCount

QUERY_COUNT = 5

class Client:
    def __init__(self):
        self._working = True
        self._queriesReceived = set()
        self._maxData = int(os.getenv('MAX_DATA_BYTES'))
        self._communication = ClientCommunication()

    def isRunning(self):
        return self._working
    
    def stopWorking(self):
        self._working = False

    def shutdown(self):
        self._communication.stop()

    def sendTable(self, tableGenerator, tableType):
        self._communication.sendTable(self, self._maxData, tableGenerator, tableType)

    def isDoneReceiving(self):
        return len(self._queriesReceived) == QUERY_COUNT
    
    def receiveQuery1Answer(self, data):
        response = EntryOSCount.deserialize(data)
        logging.info(f'action: store query 1 data | data received: {response}')
        storeResultsQuery1(str(response))

    def receiveQuery2Answer(self, data, includeHeader: bool):
        receiveCSVAnswer(data, includeHeader, entryType=EntryNameAvgPlaytime, queryNum=2)

    def receiveQuery3Answer(self, data, includeHeader: bool):
        receiveCSVAnswer(data, includeHeader, entryType=EntryNameReviewCount, queryNum=3)

    def receiveQuery4Answer(self, data, includeHeader: bool):
        receiveCSVAnswer(data, includeHeader, entryType=EntryName, queryNum = 4)
        
    def receiveQuery5Answer(self, data, includeHeader: bool):
        receiveCSVAnswer(data, includeHeader, entryType=EntryAppIDName, queryNum=5)

    def processResponse(self, data: bytes, header: HeaderWithQueryNumber) -> bool:
        logging.info(f'action: receive response for query {header.getQueryNumber()} | {header} | result: success ')
        match header.getQueryNumber():
            case 1: self.receiveQuery1Answer(data)
            case 2: self.receiveQuery2Answer(data, header.getFragmentNumber() == 1)
            case 3: self.receiveQuery3Answer(data, header.getFragmentNumber() == 1)
            case 4: self.receiveQuery4Answer(data, header.getFragmentNumber() == 1)
            case 5: self.receiveQuery5Answer(data, header.getFragmentNumber() == 1)
            case default:
                raise(Exception("invalid query num"))
            
        return header.isEOF()

    def hasReceivedQueryBefore(self, header: HeaderWithQueryNumber):
        return header._queryNumber in self._queriesReceived

    def waitForResponses(self):
        while not self.isDoneReceiving() and self.isRunning():
            msg = self._communication.receiveFromServer()
            if msg == None:
                continue
            header, data = HeaderWithQueryNumber.deserialize(msg)
            if self.hasReceivedQueryBefore(header):
                continue

            if self.processResponse(data, header):
                self._queriesReceived.add(header.getQueryNumber())