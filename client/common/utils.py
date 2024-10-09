import csv
import sys
from entryParsing.gameEntry import GameEntry
from entryParsing.reviewEntry import ReviewEntry
csv.field_size_limit(sys.maxsize)

""" Games storage location. """
GAMES_STORAGE_FILEPATH = "./datasets/games-reducido.csv"

""" Reviews storage location. """
REVIEWS_STORAGE_FILEPATH = "./datasets/reviews-reducido.csv"

QUERY_RESPONSES_PATH = "."

def storeResultsQuery1(response: str) -> None:
    filepath = QUERY_RESPONSES_PATH + "/query1.txt"
    storeResultsQuery(response, filepath)

def storeResultsQuery2(response: str) -> None:
    filepath = QUERY_RESPONSES_PATH + "/query2.csv"
    storeResultsQuery(response, filepath)
    
def storeResultsQuery3(response: str) -> None:
    filepath = QUERY_RESPONSES_PATH + "/query3.csv"
    storeResultsQuery(response, filepath)
                
def storeResultsQuery4(response: str) -> None:
    filepath = QUERY_RESPONSES_PATH + "/query4.csv"
    storeResultsQuery(response, filepath)

def storeResultsQuery5(response: str) -> None:
    filepath = QUERY_RESPONSES_PATH + "/query5.csv"
    storeResultsQuery(response, filepath)
                
def storeResultsQuery(result: str, filepath: str) -> None:
    with open(filepath, 'a+') as file:
        file.write(result)
    
def loadGames() -> list[GameEntry]: # type: ignore
    with open(GAMES_STORAGE_FILEPATH, 'r') as file:
        reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
        next(reader)  # Skip header
        for line_number, row in enumerate(reader, start=2):
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

