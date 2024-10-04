import datetime
from typing import Tuple
from client.common.utils import strToBoolInt



PEAK_CCU_BYTES = 3 # INT - MAX: 1.29M
REQ_AGE_BYTES = 1
DISC_COUNT_BYTES = 1 # ALWAYS 0 IN DATASET
META_SCORE_BYTES = 1 # INT - IN RANGE: 0 - 100
USER_SCORE = 1 # INT - IN RANGE: 0 - 100
PRICE_BYTES = 4 # FLOAT - MAX: 999.98 
POSITIVE_BYTES = 3 # INT - MAX: 5.77m
NEGATIVE_BYTES = 3 # INT - MAX:  897k
ACHIVEMENT_BYTES = 2 # INT = MAX: 9821
SCORE_RANK_BYTES = 4 #FLOAT
RECS_BYTES = 3 # INT - MAX: 3.45m
AVG_PT_FRV_BYTES = 2 # INT - MAX: 47K
MEDIAN_PT_FRV_BYTES = 2 # INT - MAX: 19.2K
AVG_PT_TWO_WEEKS_BYTES = 3 # INT MAX: 208K
MEDIAN_PT_TWO_WEEKS_BYTES = 2 # INT MAX: 19.2K
BOOLEAN_LEN = 1

U8_MAX = 255
U16_MAX = 65535 #65k
U32_MAX = 4294967295

STR_LEN = 3

def serializeNumber(number, size: int) -> bytes:
    return number.to_bytes(size,'big')

def deserializeNumber(data: bytes, curr: int, numberLen: int):
    number = int.from_bytes(data[curr:curr+numberLen], 'big')
    return number, curr + numberLen

def serializeString(string: str) -> bytes:
    stringBytes = string.encode()
    stringLenBytes = len(stringBytes).to_bytes(STR_LEN, 'big')
    return stringLenBytes + stringBytes

def deserializeString(curr: int, data: bytes)-> Tuple[str, int]:
    stringLen = int.from_bytes(data[curr:curr+STR_LEN], 'big')
    curr+=STR_LEN
    string = data[curr:stringLen+curr].decode()
    return string, curr + stringLen


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
                                                  supportUrl, supportEmail, strToBoolInt(windows), strToBoolInt(mac), strToBoolInt(linux),
                                                  int(metaScore), metaUrl, int(userScore), int(positive),
                                                  int(negative), float(scoreRank), int(achievements), int(recs), notes, 
                                                  int(avgPlaytimeForever), int(avgPlaytimeTwoWeeks),
                                                  int(medianPlaytimeForever), int(medianPlaytimeTwoWeeks), devs, pubs, categories,
                                                  genres, tags, screens, movies)
        
    def serialize(self) -> bytes:
        return (serializeString(self.appID) + serializeString(self.name) +
                        serializeString(self.releaseDate) + 
                        serializeString(self.estimatedOwners) + 
                        serializeNumber(self.peakCCU, PEAK_CCU_BYTES) + serializeNumber(self.reqAge, REQ_AGE_BYTES) + serializeNumber(self.price, PRICE_BYTES) +
         serializeNumber(self.discCount,DISC_COUNT_BYTES) + 
         serializeString(self.about) + serializeString(self.supLang) + serializeString(self.audioLang) + serializeString(self.reviews) + 
         serializeString(self.headerImg) +  serializeString(self.website) + serializeString(self.supportUrl) + serializeString(self.supportEmail) + 
         serializeNumber(self.windows, BOOLEAN_LEN) + serializeNumber(self.mac, BOOLEAN_LEN) + serializeNumber(self.linux, BOOLEAN_LEN) +  
         
         serializeNumber(self.metaScore, META_SCORE_BYTES) +  
         
         serializeString(self.metaUrl) + serializeNumber(self.userScore,USER_SCORE)
        + serializeNumber(self.positive, POSITIVE_BYTES) + 
        serializeNumber(self.negative,NEGATIVE_BYTES) + serializeNumber(self.scoreRank,SCORE_RANK_BYTES) + serializeNumber(self.achievements,ACHIVEMENT_BYTES)+ serializeNumber(self.recs,RECS_BYTES) + serializeString(self.notes) + 
         serializeNumber(self.avgPlaytimeForever,AVG_PT_FRV_BYTES) + serializeNumber(self.avgPlaytimeTwoWeeks, AVG_PT_TWO_WEEKS_BYTES) + serializeNumber(self.medianPlaytimeForever,MEDIAN_PT_FRV_BYTES) + serializeNumber(self.medianPlaytimeTwoWeeks, MEDIAN_PT_TWO_WEEKS_BYTES) + 
         serializeString(self.devs) +  
         serializeString(self.pubs) + serializeString(self.categories) +  serializeString(self.genres) +
         serializeString(self.tags) + serializeString(self.screens) + serializeString(self.movies))

