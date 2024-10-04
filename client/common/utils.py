import csv

from client.common.queryResponses import GamesNamesResponse, Query1Response, Query2Response, Query3Response, Query4Response

""" Games storage location. """
GAMES_STORAGE_FILEPATH = ""

""" Reviews storage location. """
REVIEWS_STORAGE_FILEPATH = ""

QUERY_RESPONSES_PATH = ""

        
def strToBoolInt(string: str) -> int:
    match string: 
        case "True":
            return 0
        case "False":
            return 1
        case _:
            raise(Exception("Boolean field could not be converted"))

"""
Persist the information of each row returned by the query 1
Not thread-safe/process-safe.
"""
def storeResultsQuery1(results: 'Query1Response') -> None:
    filepath = QUERY_RESPONSES_PATH + "/query1"
    with open(filepath, 'a+') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        for res in results: 
            writer.writerow([res.OSCount])
            

"""
Persist the information of each row returned by the query 1
Not thread-safe/process-safe.
"""
def storeResultsQuery2(result: 'Query2Response') -> None:
    filepath = QUERY_RESPONSES_PATH + "/query2"
    storeResultsGameNames(result, filepath)


"""
Persist the information of each row returned by the query 1
Not thread-safe/process-safe.
"""
def storeResultsQuery4(result: 'Query3Response') -> None:
    filepath = QUERY_RESPONSES_PATH + "/query3"
    storeResultsGameNames(result, filepath)
            
             

"""
Persist the information of each row returned by the query 1
Not thread-safe/process-safe.
"""
def storeResultsQuery4(result: 'Query4Response') -> None:
    filepath = QUERY_RESPONSES_PATH + "/query4"
    storeResultsGameNames(result, filepath)
           
            
def storeResultsGameNames(result: 'GamesNamesResponse' , filepath) -> None:
    with open(filepath, 'a+') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        for res in result.gamesNames: 
            writer.writerow([res])
      
            


"""
Loads the information all the bets in the STORAGE_FILEPATH file.
Not thread-safe/process-safe.
"""
def loadGames() -> list[Game]:
    with open(GAMES_STORAGE_FILEPATH, 'r') as file:
        reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            yield Game(row[0], row[1], row[2], row[3], row[4], row[5],
                       row[6], row[7], row[9], row[10], row[11], row[12],
                       row[13], row[14], row[15], row[16], row[17], row[18],
                       row[19], row[20], row[21], row[22], row[23], row[24],
                       row[25], row[26], row[27], row[28], row[29], row[30],
                       row[31], row[32], row[33], row[34], row[35], row[36],
                       row[37], row[38], row[39])

