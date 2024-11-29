from entryParsing.common.fieldParsing import  floatToInt, parseDate, serializeAppID, serializeGameName, serializeNumber, serializePlaytime, serializeReviewText, serializeVariableLen, tryToFloat
from entryParsing.common.utils import strToBoolInt
from entryParsing.common import fieldLen
from entryParsing.entry import EntryInterface            

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
    
    @classmethod    
    def deserialize(cls, data: bytes) -> list['GameEntry']:
        raise Exception("The should be no need to deserialize this type of entry")