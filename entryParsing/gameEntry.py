import datetime

from entryParsing.common.fieldParsing import BOOLEAN_LEN, deserializeAppID, deserializeGameName, deserializeNumber, deserializePlaytime, deserializeReviewText, deserializeVariableLen, serializeAppID, serializeGameName, serializeNumber, serializePlaytime, serializeReviewText, serializeVariableLen
from entryParsing.common.utils import strToBoolInt
from entryParsing.entry import EntryInterface

PEAK_CCU_BYTES = 3, REQ_AGE_BYTES = 1, DISC_COUNT_BYTES = 1 
META_SCORE_BYTES = 1 , USER_SCORE_BYTES = 1 
PRICE_BYTES = 4, POSITIVE_BYTES = 3, NEGATIVE_BYTES = 3
ACHIVEMENT_BYTES = 2, SCORE_RANK_BYTES = 4, RECS_BYTES = 3
MEDIAN_BYTES = 2 
DATE_LEN = 1, EST_OWN_LEN = 1, ABOUT_LEN = 3
LANG_LEN = 2, URL_LEN = 2, NOTES_LEN = 2, TEAM_LEN = 2, MEDIA_LEN = 2,GENRE_LEN = 2

class GameEntry(EntryInterface):
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
        return (serializeAppID(self.appID) + serializeGameName(self.name) + serializeVariableLen(self.releaseDate, DATE_LEN) + 
                serializeVariableLen(self.estimatedOwners, EST_OWN_LEN) + serializeNumber(self.peakCCU, PEAK_CCU_BYTES) + 
                serializeNumber(self.reqAge, REQ_AGE_BYTES) + serializeNumber(self.price, PRICE_BYTES) + serializeNumber(self.discCount,DISC_COUNT_BYTES) + 
                serializeVariableLen(self.about, ABOUT_LEN) + serializeVariableLen(self.supLang, LANG_LEN) + serializeVariableLen(self.audioLang, LANG_LEN) + 
                serializeReviewText(self.reviews) + serializeVariableLen(self.headerImg, MEDIA_LEN) +  serializeVariableLen(self.website, URL_LEN) + 
                serializeVariableLen(self.supportUrl, URL_LEN) + serializeVariableLen(self.supportEmail, URL_LEN) + serializeNumber(self.windows, BOOLEAN_LEN) + 
                serializeNumber(self.mac, BOOLEAN_LEN) + serializeNumber(self.linux, BOOLEAN_LEN) + serializeNumber(self.metaScore, META_SCORE_BYTES) +  
                serializeVariableLen(self.metaUrl, URL_LEN) + serializeNumber(self.userScore,USER_SCORE_BYTES) + serializeNumber(self.positive, POSITIVE_BYTES) + 
                serializeNumber(self.negative,NEGATIVE_BYTES) + serializeNumber(self.scoreRank,SCORE_RANK_BYTES) + serializeNumber(self.achievements,ACHIVEMENT_BYTES)+ 
                serializeNumber(self.recs,RECS_BYTES) + serializeVariableLen(self.notes, NOTES_LEN) + serializePlaytime(self.avgPlaytimeForever) + 
                serializePlaytime(self.avgPlaytimeTwoWeeks) + serializeNumber(self.medianPlaytimeForever,MEDIAN_BYTES) + serializeNumber(self.medianPlaytimeTwoWeeks, MEDIAN_BYTES) + 
                serializeVariableLen(self.devs, TEAM_LEN) +  serializeVariableLen(self.pubs, TEAM_LEN) + serializeVariableLen(self.categories, GENRE_LEN) +  
                serializeVariableLen(self.genres, GENRE_LEN) + serializeVariableLen(self.tags, GENRE_LEN) + serializeVariableLen(self.screens, MEDIA_LEN) + serializeVariableLen(self.movies, MEDIA_LEN)
                )
    
    def serializeForQuery1(self) -> bytes:
        return serializeNumber(self.windows, BOOLEAN_LEN) + serializeNumber(self.mac, BOOLEAN_LEN) + serializeNumber(self.linux, BOOLEAN_LEN)
    
    def serializeForQuery2And3(self) -> bytes:
        return serializeAppID(self.appID) + serializeGameName(self.name) + serializeVariableLen(self.genres, GENRE_LEN) + serializeVariableLen(self.releaseDate, DATE_LEN) + serializePlaytime(self.avgPlaytimeForever)

    def serializeForQuery4And5(self) -> bytes:
        return serializeAppID(self.appID) + serializeGameName(self.name) + serializeVariableLen(self.genres, GENRE_LEN)

    @classmethod
    def deserialize(cls, data: bytes)-> list['GameEntry']:
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                appID, curr = deserializeAppID(data, curr)
                name, curr = deserializeGameName(data, curr)
                releaseDate, curr = deserializeVariableLen(data,curr, DATE_LEN)
                estimatedOwners, curr = deserializeVariableLen(data,curr, EST_OWN_LEN)
                peakCCU, curr = deserializeNumber(data,curr, PEAK_CCU_BYTES)
                reqAge, curr = deserializeNumber(data,curr, REQ_AGE_BYTES)
                price, curr = deserializeNumber(data,curr, PRICE_BYTES)
                discCount, curr = deserializeNumber(data,curr, DISC_COUNT_BYTES)
                about, curr = deserializeVariableLen(data,curr, ABOUT_LEN)
                supLang, curr = deserializeVariableLen(data,curr, LANG_LEN)
                audioLang, curr = deserializeVariableLen(data,curr, LANG_LEN)
                reviews, curr = deserializeReviewText(data,curr)
                headerImg, curr = deserializeVariableLen(data,curr, MEDIA_LEN)
                website, curr = deserializeVariableLen(data,curr, URL_LEN)
                supportUrl, curr = deserializeVariableLen(data,curr, URL_LEN)
                supportEmail, curr = deserializeVariableLen(data,curr, URL_LEN)
                windows, curr = deserializeNumber(data,curr, BOOLEAN_LEN)
                mac, curr = deserializeNumber(data,curr, BOOLEAN_LEN)
                linux, curr = deserializeNumber(data,curr, BOOLEAN_LEN)
                metaScore, curr = deserializeNumber(data,curr, META_SCORE_BYTES)
                metaUrl, curr = deserializeVariableLen(data,curr, URL_LEN)
                userScore, curr = deserializeNumber(data,curr, USER_SCORE_BYTES)
                positive, curr = deserializeNumber(data,curr, POSITIVE_BYTES)
                negative, curr = deserializeNumber(data,curr, NEGATIVE_BYTES)
                scoreRank, curr = deserializeNumber(data,curr, SCORE_RANK_BYTES)
                achievements, curr = deserializeNumber(data,curr, ACHIVEMENT_BYTES)
                recs, curr = deserializeNumber(data,curr, RECS_BYTES)
                notes, curr = deserializeVariableLen(data,curr, NOTES_LEN)
                avgPlaytimeForever, curr = deserializePlaytime(data,curr)
                avgPlaytimeTwoWeeks, curr = deserializePlaytime(data,curr)
                medianPlaytimeForever, curr = deserializeNumber(data,curr, MEDIAN_BYTES)
                medianPlaytimeTwoWeeks, curr = deserializeNumber(data,curr, MEDIAN_BYTES)
                devs, curr = deserializeVariableLen(data,curr, TEAM_LEN)
                pubs, curr = deserializeVariableLen(data,curr, TEAM_LEN)
                categories, curr = deserializeVariableLen(data,curr, GENRE_LEN)
                genres, curr = deserializeVariableLen(data,curr, GENRE_LEN)
                tags, curr = deserializeVariableLen(data,curr, GENRE_LEN)
                screens, curr = deserializeVariableLen(data,curr, MEDIA_LEN)
                movies, curr =  deserializeVariableLen(data,curr, MEDIA_LEN)
                entries.append(GameEntry(appID, name, releaseDate, estimatedOwners, peakCCU, reqAge, price, discCount, about,
                                         supLang, audioLang, reviews, headerImg, website, supportUrl, supportEmail,
                                         windows, mac, linux, metaScore, metaUrl, userScore, positive, negative, scoreRank, achievements,
                                         recs, notes, avgPlaytimeForever, avgPlaytimeTwoWeeks, medianPlaytimeForever, medianPlaytimeTwoWeeks,
                                         devs, pubs, categories, genres, tags, screens, movies))
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")
        return entries
