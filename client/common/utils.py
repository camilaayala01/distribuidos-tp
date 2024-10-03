import csv
import datetime
import time

from client.common.queryResponses import GamesNamesResponse, Query1Response, Query2Response, Query3Response, Query4Response, query1Response, query2Response, query3Response, query4Response


""" Games storage location. """
GAMES_STORAGE_FILEPATH = ""

""" Reviews storage location. """
REVIEWS_STORAGE_FILEPATH = ""

QUERY_RESPONSES_PATH = ""

def strToBool(string: str) -> bool:
    match string: 
        case "True":
            return True
        case "False":
            return False
        case _:
            raise(Exception("Boolean field could not be converted"))
""" An entry of the steam games dataset. """
class Game:
    def __init__(self, appID, name, releaseDate, estimatedOwners, peakCCU, reqAge, price, discCount, about, supLang, 
                 audioLang, reviews, headerImg, website, supportUrl, supportEmail, windows, mac, linux, metaScore, metaUrl, 
                 userScore, positive, negative, scoreRank, achievements, recs, notes, avgPlaytimeForever, avgPlaytimeTwoWeeks,
                 medianPlaytimeForever, medianPlaytimeTwoWeeks, devs, pubs, categories, genres, tags, screens, movies):
        """
        releaseDate must be passed with format: 'Month Day, Year'.
        windows, mac and linux must be passed with boolean format
        The following must be passed with integer format: peakCCU, reqAge, discCount, metaScore, userScore, positive, negative, achievements, recs
        avgPlaytimeForever, avgPlaytimeTwoWeeks, medianPlaytimeForever, medianPlaytimeTwoWeeks
        price and scoreRank must be passed with float format
        """
        (self.appID, self.name, self.releaseDate, self.estimatedOwners, self.peakCCU, self.reqAge, self.price,
         self.discCount, self.about, self.supLang, self.audioLang, self.reviews, 
         self.headerImg, self.website, self.supportUrl, self.supportEmail, self.windows, self.mac, self.linux, self.metaScore, 
         self.metaUrl,self.userScore, self.positive, self.negative, self.scoreRank, self.achievements, self.recs, self.notes, 
         self.avgPlaytimeForever, self.avgPlaytimeTwoWeeks,self.medianPlaytimeForever, self.medianPlaytimeTwoWeeks, self.devs, 
         self.pubs, self.categories, self.genres,
         self.tags, self.screens, self.movies) = (appID, name, datetime.strptime(releaseDate, "%b %d, %Y").strftime("%d-%m-%Y"), 
                                                  estimatedOwners, int(peakCCU), int(reqAge), float(price), int(discCount), 
                                                  about, supLang, audioLang ,reviews, headerImg, website,
                                                  supportUrl, supportEmail, strToBool(windows), strToBool(mac), strToBool(linux),
                                                  int(metaScore), metaUrl, int(userScore), int(positive),
                                                  int(negative), float(scoreRank), int(achievements), int(recs), notes, 
                                                  int(avgPlaytimeForever), int(avgPlaytimeTwoWeeks),
                                                  int(medianPlaytimeForever), int(medianPlaytimeTwoWeeks), devs, pubs, categories,
                                                  genres, tags, screens, movies)



"""
Persist the information of each row returned by the query 1
Not thread-safe/process-safe.
"""
def storeResultsQuery1(results: 'Query1Response') -> None:
    filepath = QUERY_RESPONSES_PATH + "/query1"
    with open(filepath, 'a+') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        for res in results: 
            writer.writerow([res.windowsCount, res.macCount, res.linuxCount])
            

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
