import datetime

from entryParsing.common.fieldParsing import  serializeAppID, serializeGameName, serializeNumber, serializePlaytime, serializeReviewText, serializeVariableLen
from entryParsing.common.utils import strToBoolInt
from entryParsing.common import fieldLen
from entryParsing.entry import EntryInterface

def floatToInt(number) -> int:
    return int(number * 100)
        
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
            

class GameEntry(EntryInterface):
    def __init__(self, _appID, _name, _releaseDate, _estimatedOwners, _peakCCU, _reqAge, _price, _discCount, 
                 _about, _supLang, _audioLang, _reviews, _headerImg, _website, _supportUrl, _supportEmail, 
                 _windows, _mac, _linux, _metaScore, _metaUrl, _userScore, _positive, _negative, 
                 _scoreRank, _achievements, _recs, _notes, _avgPlaytime, _avgPlaytimeTwoWeeks,
                 _medianPlaytimeForever, _medianPlaytimeTwoWeeks, _devs, _pubs, _categories, 
                 _genres, _tags, _screens, _movies):
        """
        releaseDate must be passed with format: 'Month Day, Year'.
        windows, mac and linux must be passed with boolean format
        The following must be passed with integer format: peakCCU, reqAge, discCount, metaScore, userScore, positive, negative, achievements, recs
        avgPlaytimeForever, avgPlaytimeTwoWeeks, medianPlaytimeForever, medianPlaytimeTwoWeeks
        price and scoreRank must be passed with float format
        """
        super().__init__(_appID=_appID, _name=_name, _releaseDate=parseDate(_releaseDate), 
                         _estimatedOwners=_estimatedOwners, _peakCCU=int(_peakCCU), _reqAge=int(_reqAge), 
                         _price=tryToFloat(_price), _discCount=int(_discCount), _about=_about, 
                         _supLang=_supLang, _audioLang=_audioLang, _reviews=_reviews, 
                         _headerImg=_headerImg, _website=_website, _supportUrl=_supportUrl, 
                         _supportEmail=_supportEmail, _windows=strToBoolInt(_windows), 
                         _mac=strToBoolInt(_mac), _linux=strToBoolInt(_linux), 
                         _metaScore=int(_metaScore), _metaUrl=_metaUrl, _userScore=int(_userScore), 
                         _positive=int(_positive), _negative=int(_negative), 
                         _scoreRank=tryToFloat(_scoreRank), _achievements=int(_achievements), 
                         _recs=int(_recs), _notes=_notes, _avgPlaytime=int(_avgPlaytime), 
                         _avgPlaytimeTwoWeeks=int(_avgPlaytimeTwoWeeks), 
                         _medianPlaytimeForever=int(_medianPlaytimeForever), 
                         _medianPlaytimeTwoWeeks=int(_medianPlaytimeTwoWeeks), _devs=_devs, 
                         _pubs=_pubs, _categories=_categories, _genres=_genres, 
                         _tags=_tags, _screens=_screens, _movies=_movies)
       
        
    def serialize(self) -> bytes:
        return (
            serializeAppID(self._appID) +
            serializeGameName(self._name) +
            serializeVariableLen(self._releaseDate, fieldLen.DATE_LEN) +
            serializeVariableLen(self._estimatedOwners, fieldLen.EST_OWN_LEN) +
            serializeNumber(self._peakCCU, fieldLen.PEAK_CCU_BYTES) +
            serializeNumber(self._reqAge, fieldLen.REQ_AGE_BYTES) +
            serializeNumber(floatToInt(self._price), fieldLen.PRICE_BYTES) +
            serializeNumber(self._discCount, fieldLen.DISC_COUNT_BYTES) +
            serializeVariableLen(self._about, fieldLen.ABOUT_LEN) +
            serializeVariableLen(self._supLang, fieldLen.LANG_LEN) +
            serializeVariableLen(self._audioLang, fieldLen.LANG_LEN) +
            serializeReviewText(self._reviews) +
            serializeVariableLen(self._headerImg, fieldLen.MEDIA_LEN) +
            serializeVariableLen(self._website, fieldLen.URL_LEN) +
            serializeVariableLen(self._supportUrl, fieldLen.URL_LEN) +
            serializeVariableLen(self._supportEmail, fieldLen.URL_LEN) +
            serializeNumber(self._windows, fieldLen.BOOLEAN_LEN) +
            serializeNumber(self._mac, fieldLen.BOOLEAN_LEN) +
            serializeNumber(self._linux, fieldLen.BOOLEAN_LEN) +
            serializeNumber(self._metaScore, fieldLen.META_SCORE_BYTES) +
            serializeVariableLen(self._metaUrl, fieldLen.URL_LEN) +
            serializeNumber(self._userScore, fieldLen.USER_SCORE_BYTES) +
            serializeNumber(self._positive, fieldLen.POSITIVE_BYTES) +
            serializeNumber(self._negative, fieldLen.NEGATIVE_BYTES) +
            serializeNumber(floatToInt(self._scoreRank), fieldLen.SCORE_RANK_BYTES) +
            serializeNumber(self._achievements, fieldLen.ACHIVEMENT_BYTES) +
            serializeNumber(self._recs, fieldLen.RECS_BYTES) +
            serializeVariableLen(self._notes, fieldLen.NOTES_LEN) +
            serializePlaytime(self._avgPlaytime) +
            serializePlaytime(self._avgPlaytimeTwoWeeks) +
            serializeNumber(self._medianPlaytimeForever, fieldLen.MEDIAN_BYTES) +
            serializeNumber(self._medianPlaytimeTwoWeeks, fieldLen.MEDIAN_BYTES) +
            serializeVariableLen(self._devs, fieldLen.TEAM_LEN) +
            serializeVariableLen(self._pubs, fieldLen.TEAM_LEN) +
            serializeVariableLen(self._categories, fieldLen.GENRE_LEN) +
            serializeVariableLen(self._genres, fieldLen.GENRE_LEN) +
            serializeVariableLen(self._tags, fieldLen.GENRE_LEN) +
            serializeVariableLen(self._screens, fieldLen.MEDIA_LEN) +
            serializeVariableLen(self._movies, fieldLen.MEDIA_LEN)
        )

    
    @classmethod    
    def deserialize(cls, data: bytes) -> list['GameEntry']:
        raise Exception("The should be no need to deserialize this type of entry")