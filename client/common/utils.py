import csv

from entryParsing.entryOSCount import EntryOSCount
from entryParsing.gameEntry import GameEntry
from entryParsing.reviewEntry import ReviewEntry

""" Games storage location. """
GAMES_STORAGE_FILEPATH = "./datasets/games.csv"

""" Reviews storage location. """
REVIEWS_STORAGE_FILEPATH = "./datasets/dataset.csv"

QUERY_RESPONSES_PATH = "./responses"

"""
Only called once. Not a CSV
"""
def storeResultsQuery1(response: str) -> None:
    filepath = QUERY_RESPONSES_PATH + "/query1.txt"
    with open(filepath, 'a+') as file:
        file.write(response)
    
        
"""
Persist the information of each response for query 2 from a batch 
Not thread-safe/process-safe.
"""
def storeResultsQuery2(result: 'Query2Response') -> None:
    filepath = QUERY_RESPONSES_PATH + "/query2.csv"
    


"""
Persist the information of each response for query 3 from a batch 
Not thread-safe/process-safe.
"""
def storeResultsQuery4(result: 'Query3Response') -> None:
    filepath = QUERY_RESPONSES_PATH + "/query3.csv"
    
            
            
"""
Persist the information of each response for query 4 from a batch 
Not thread-safe/process-safe.
"""
def storeResultsQuery4(result: 'Query4Response') -> None:
    filepath = QUERY_RESPONSES_PATH + "/query4.csv"
    with open(filepath, 'a+') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        for res in result.gamesNames: 
            writer.writerow([res])
           
        
    
      
        
"""
Loads the information all the bets in the STORAGE_FILEPATH file.
Not thread-safe/process-safe.
"""
import sys

csv.field_size_limit(sys.maxsize)

def loadGames() -> list[GameEntry]:
    with open(GAMES_STORAGE_FILEPATH, 'r') as file:
        reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
        next(reader)  # Skip header
        for line_number, row in enumerate(reader, start=2):
            try:
                #if line_number not in [94, 147, 538, 1247, 1466, 1593, 1930, 1992, 2074, 2466]:
                yield GameEntry(row[0], row[1], row[2], row[3], row[4], row[5],
                                row[6], row[7], row[9], row[10], row[11], row[12],
                                row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24],
                                row[25], row[26], row[27], row[28], row[29], row[30],
                                row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39])
    
            except StopIteration:
                return None
            except Exception as e:
                print(f"Error on line {line_number}: {e}")
                return

            

"""
Loads the information all the bets in the STORAGE_FILEPATH file.
Not thread-safe/process-safe.
"""
def loadReviews() -> list[ReviewEntry]:
    with open(REVIEWS_STORAGE_FILEPATH, 'r') as file:
        reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
        next(reader) #skip header
        for row in reader:
            try:
                yield ReviewEntry(row[0], row[1], row[2], row[3], row[4])
            except StopIteration:
                return None
            except Exception as e:
                print(e)
                return

