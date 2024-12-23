import csv
import logging
import os
import sys
from entryParsing.fullEntry import GameEntry, ReviewEntry
csv.field_size_limit(sys.maxsize)

""" Games storage location. """
GAMES_STORAGE_FILEPATH = os.getenv('GAMES_STORAGE_FILEPATH')

""" Reviews storage location. """
REVIEWS_STORAGE_FILEPATH = os.getenv('REVIEWS_STORAGE_FILEPATH')

QUERY_RESPONSES_PATH = "/responses/"

def receiveCSVAnswer(data, includeHeader: bool, entryType, queryNum, currentExecution):
    if includeHeader:
        storeHeader(entryType.header(), f'exec-{currentExecution}/query{queryNum}.csv')
    responses = entryType.deserialize(data)
    csvData, loggingData = "", ""
    for response in responses:
        csvData += response.csv()
        loggingData += str(response)
    logging.info(f'action: store query {queryNum} data | data received: {loggingData}')
    storeResultsQuery(csvData, f'exec-{currentExecution}/query{queryNum}.csv')

def storeResultsQuery1(response: str, currentExecution) -> None:
    filepath = QUERY_RESPONSES_PATH + f'exec-{currentExecution}/query1.txt'
    with open(filepath, 'w+') as file:
        file.write(response)

def storeHeader(header: str, filepath: str):
    path = QUERY_RESPONSES_PATH + filepath
    with open(path, 'w+') as file:
        file.write(header)
                
def storeResultsQuery(result: str, filepath: str) -> None:
    path = QUERY_RESPONSES_PATH + filepath
    with open(path, 'a+') as file:
        file.write(result)
    
def loadGames() -> list[GameEntry]: # type: ignore
    with open(GAMES_STORAGE_FILEPATH, 'r') as file:
        reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
        next(reader)  # Skip header
        for row in reader:
            try:
                yield GameEntry(row[0], row[1], row[2], row[3], row[4], row[5],
                                row[6], row[7], row[9], row[10], row[11], row[12],
                                row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24],
                                row[25], row[26], row[27], row[28], row[29], row[30],
                                row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39])
    
            except Exception as e:
                pass
            
def loadReviews() -> list[ReviewEntry]: # type: ignore
    with open(REVIEWS_STORAGE_FILEPATH, 'r') as file:
        reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
        next(reader) #skip header
        for row in reader:
            try:
                yield ReviewEntry(row[0], row[1], row[2], row[3], row[4])
            except StopIteration:
                return None
            except Exception as e:
                pass

