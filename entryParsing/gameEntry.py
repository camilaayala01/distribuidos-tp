import datetime

from entryParsing.common.fieldParsing import serializeBoolean, serializeAppID, serializeGameName, serializeNumber, serializePlaytime, serializeReviewText, serializeVariableLen
from entryParsing.common.utils import strToBoolInt
from entryParsing.common import fieldLen

def floatToInt(number) -> int:
    return int(number * 100)

def floatFromInt(number)-> float:
    return float(number / 100)
        
def tryToFloat(string)-> float:
    try: 
        return float(string)
    except Exception:
        return 0
    
def parseDate(string)-> datetime.datetime:
    try:
        return datetime.datetime.strptime(string,"%b %d, %Y").strftime("%d-%m-%Y")
    except Exception:
        return datetime.datetime.strptime("1 " + string, "%d %b %Y").strftime("%d-%m-%Y")
            

class GameEntry():
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
            self.tags, self.screens, self.movies) = (appID, name, parseDate(releaseDate), 
                                                    estimatedOwners, int(peakCCU), int(reqAge), tryToFloat(price), int(discCount), 
                                                    about, supLang, audioLang ,reviews, headerImg, website,
                                                    supportUrl, supportEmail, strToBoolInt(windows), strToBoolInt(mac), strToBoolInt(linux),
                                                    int(metaScore), metaUrl, int(userScore), int(positive),
                                                    int(negative), tryToFloat(scoreRank), int(achievements), int(recs), notes, 
                                                    int(avgPlaytimeForever), int(avgPlaytimeTwoWeeks),
                                                    int(medianPlaytimeForever), int(medianPlaytimeTwoWeeks), devs, pubs, categories,
                                                    genres, tags, screens, movies)
       
        
    def serialize(self) -> bytes:
        return (serializeAppID(self.appID) + serializeGameName(self.name) + serializeVariableLen(self.releaseDate, fieldLen.DATE_LEN) + 
                serializeVariableLen(self.estimatedOwners, fieldLen.EST_OWN_LEN) + serializeNumber(self.peakCCU, fieldLen.PEAK_CCU_BYTES) + 
                serializeNumber(self.reqAge, fieldLen.REQ_AGE_BYTES) + serializeNumber(floatToInt(self.price), fieldLen.PRICE_BYTES) + serializeNumber(self.discCount, fieldLen.DISC_COUNT_BYTES) + 
                serializeVariableLen(self.about, fieldLen.ABOUT_LEN) + serializeVariableLen(self.supLang, fieldLen.LANG_LEN) + serializeVariableLen(self.audioLang, fieldLen.LANG_LEN) + 
                serializeReviewText(self.reviews) + serializeVariableLen(self.headerImg, fieldLen.MEDIA_LEN) +  serializeVariableLen(self.website, fieldLen.URL_LEN) + 
                serializeVariableLen(self.supportUrl, fieldLen.URL_LEN) + serializeVariableLen(self.supportEmail, fieldLen.URL_LEN) + serializeNumber(self.windows, fieldLen.BOOLEAN_LEN) + 
                serializeNumber(self.mac, fieldLen.BOOLEAN_LEN) + serializeNumber(self.linux, fieldLen.BOOLEAN_LEN) + serializeNumber(self.metaScore, fieldLen.META_SCORE_BYTES) +  
                serializeVariableLen(self.metaUrl, fieldLen.URL_LEN) + serializeNumber(self.userScore, fieldLen.USER_SCORE_BYTES) + serializeNumber(self.positive, fieldLen.POSITIVE_BYTES) + 
                serializeNumber(self.negative, fieldLen.NEGATIVE_BYTES) + serializeNumber(floatToInt(self.scoreRank), fieldLen.SCORE_RANK_BYTES) + serializeNumber(self.achievements, fieldLen.ACHIVEMENT_BYTES)+ 
                serializeNumber(self.recs, fieldLen.RECS_BYTES) + serializeVariableLen(self.notes, fieldLen.NOTES_LEN) + serializePlaytime(self.avgPlaytimeForever) + 
                serializePlaytime(self.avgPlaytimeTwoWeeks) + serializeNumber(self.medianPlaytimeForever, fieldLen.MEDIAN_BYTES) + serializeNumber(self.medianPlaytimeTwoWeeks, fieldLen.MEDIAN_BYTES) + 
                serializeVariableLen(self.devs, fieldLen.TEAM_LEN) +  serializeVariableLen(self.pubs, fieldLen.TEAM_LEN) + serializeVariableLen(self.categories, fieldLen.GENRE_LEN) +  
                serializeVariableLen(self.genres, fieldLen.GENRE_LEN) + serializeVariableLen(self.tags, fieldLen.GENRE_LEN) + serializeVariableLen(self.screens, fieldLen.MEDIA_LEN) + serializeVariableLen(self.movies, fieldLen.MEDIA_LEN)
                )