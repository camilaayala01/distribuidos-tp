from entryParsing.common import fieldParsing, fieldLen
from entryParsing.messagePart import MessagePartInterface

"""
This entry is used by the initializer in order to skip the unnecessary fields coming from
the client. It implements its own deserialization as skipping fields is not contemplated 
in the base class.
"""
class ReducedGameEntry(MessagePartInterface):
    def __init__(self, _appID, _name, _releaseDate, _windows, _mac, _linux, _avgPlaytime, _genres):
        super().__init__(_appID=_appID, _name=_name, _releaseDate=_releaseDate,
                         _windows=_windows, _mac=_mac, _linux=_linux,
                         _avgPlaytime=_avgPlaytime, _genres=_genres)
    
    @classmethod
    def deserialize(cls, data: bytes)-> list['ReducedGameEntry']:
        curr = 0
        entries = []
        
        while len(data) > curr:
            try:
                appID, curr = fieldParsing.deserializeAppID(curr, data)
                name, curr = fieldParsing.deserializeGameName(curr, data)
                releaseDate, curr = fieldParsing.deserializeReleaseDate(curr, data)
                
                # skip unused variable len fields
                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.EST_OWN_LEN)
                # skip numeric fields
                nextCurr = curr + fieldLen.PEAK_CCU_BYTES + fieldLen.REQ_AGE_BYTES + fieldLen.PRICE_BYTES + fieldLen.DISC_COUNT_BYTES
                curr = nextCurr
                # skip more unused variable len fields
                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.ABOUT_LEN)
                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.LANG_LEN)
                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.LANG_LEN)

                curr = fieldParsing.skipReviewText(curr, data)

                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.MEDIA_LEN)
                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.URL_LEN)
                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.URL_LEN)
                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.URL_LEN)

                # keep this booleans
                windows, curr = fieldParsing.deserializeBoolean(curr, data)
                mac, curr = fieldParsing.deserializeBoolean(curr, data)
                linux, curr = fieldParsing.deserializeBoolean(curr, data)

                # more metadata to skip, many numbers
                curr += fieldLen.META_SCORE_BYTES
                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.URL_LEN)
                nextCurr = curr + fieldLen.USER_SCORE_BYTES + fieldLen.POSITIVE_BYTES + fieldLen.NEGATIVE_BYTES + fieldLen.SCORE_RANK_BYTES + fieldLen.ACHIVEMENT_BYTES + fieldLen.RECS_BYTES
                curr = nextCurr
                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.NOTES_LEN)
    
                avgPlaytimeForever, curr = fieldParsing.deserializePlaytime(curr, data)

                curr = fieldParsing.skipPlaytime(curr)
                curr += fieldLen.MEDIAN_BYTES * 2
                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.TEAM_LEN)
                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.TEAM_LEN)
                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.GENRE_LEN)

                genres, curr = fieldParsing.deserializeGenres(curr, data)

                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.GENRE_LEN)
                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.MEDIA_LEN)
                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.MEDIA_LEN)
                
                entries.append(ReducedGameEntry(appID, name, releaseDate, windows, mac, linux, avgPlaytimeForever, genres))
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")
        return entries