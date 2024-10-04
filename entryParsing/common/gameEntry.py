import datetime

from entryParsing.common.fieldParsing import APP_ID_LEN, NAME_LEN, serializeNumber, serializeString
from entryParsing.common.utils import strToBoolInt

PEAK_CCU_BYTES = 3, REQ_AGE_BYTES = 1, DISC_COUNT_BYTES = 1 
META_SCORE_BYTES = 1 , USER_SCORE = 1 
PRICE_BYTES = 4 
POSITIVE_BYTES = 3, NEGATIVE_BYTES = 3
ACHIVEMENT_BYTES = 2, SCORE_RANK_BYTES = 4, RECS_BYTES = 3
MEDIAN_PT_FRV_BYTES = 2, MEDIAN_PT_TWO_WEEKS_BYTES = 2 
AVG_PT_FRV_BYTES = 3, AVG_PT_TWO_WEEKS_BYTES = 3 # 
BOOLEAN_LEN = 1
DATE_LEN = 1, EST_OWN_LEN = 1
ABOUT_LEN = 3
LANG_LEN = 2, URL_LEN = 2, NOTES_LEN = 2, TEAM_LEN = 2, MEDIA_LEN = 2,GENRE_LEN = 2

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
        return (serializeString(self.appID, APP_ID_LEN) + serializeString(self.name, NAME_LEN) +
                        serializeString(self.releaseDate, DATE_LEN) + 
                        serializeString(self.estimatedOwners, EST_OWN_LEN) + 
                        serializeNumber(self.peakCCU, PEAK_CCU_BYTES) + serializeNumber(self.reqAge, REQ_AGE_BYTES) + serializeNumber(self.price, PRICE_BYTES) +
         serializeNumber(self.discCount,DISC_COUNT_BYTES) + 
         serializeString(self.about, ABOUT_LEN) + serializeString(self.supLang, LANG_LEN) + serializeString(self.audioLang, LANG_LEN) + serializeString(self.reviews, REV_LEN) + 
         serializeString(self.headerImg, MEDIA_LEN) +  serializeString(self.website, MEDIA_LEN) + serializeString(self.supportUrl, URL_LEN) + serializeString(self.supportEmail, URL_LEN) + 
         serializeNumber(self.windows, BOOLEAN_LEN) + serializeNumber(self.mac, BOOLEAN_LEN) + serializeNumber(self.linux, BOOLEAN_LEN) +  
         serializeNumber(self.metaScore, META_SCORE_BYTES) +  
         serializeString(self.metaUrl, URL_LEN) + serializeNumber(self.userScore,USER_SCORE)
        + serializeNumber(self.positive, POSITIVE_BYTES) + 
        serializeNumber(self.negative,NEGATIVE_BYTES) + serializeNumber(self.scoreRank,SCORE_RANK_BYTES) + serializeNumber(self.achievements,ACHIVEMENT_BYTES)+ serializeNumber(self.recs,RECS_BYTES) + serializeString(self.notes, NOTES_LEN) + 
         serializeNumber(self.avgPlaytimeForever,AVG_PT_FRV_BYTES) + serializeNumber(self.avgPlaytimeTwoWeeks, AVG_PT_TWO_WEEKS_BYTES) + serializeNumber(self.medianPlaytimeForever,MEDIAN_PT_FRV_BYTES) + serializeNumber(self.medianPlaytimeTwoWeeks, MEDIAN_PT_TWO_WEEKS_BYTES) + 
         serializeString(self.devs, TEAM_LEN) +  
         serializeString(self.pubs, TEAM_LEN) + serializeString(self.categories, GENRE_LEN) +  serializeString(self.genres, GENRE_LEN) +
         serializeString(self.tags, GENRE_LEN) + serializeString(self.screens, MEDIA_LEN) + serializeString(self.movies, MEDIA_LEN))



