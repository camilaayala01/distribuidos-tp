from entryParsing.common import fieldParsing, fieldLen
from entryParsing.gameEntry import *

class ReducedGameEntry:
    def __init__(self, appID, name, releaseDate, windows, linux, mac, avgPlaytime, genres):
        self.appID = appID
        self.name = name
        self.releaseDate = releaseDate
        self.windows = windows
        self.linux = linux
        self.mac = mac
        self.avgPlaytime = avgPlaytime
        self.genres = genres

    @classmethod
    def deserialize(cls, data: bytes)-> list['ReducedGameEntry']:
        curr = 0
        entries = []
        
        while len(data) > curr:
            try:
                appID, curr = fieldParsing.deserializeAppID(curr, data)
                name, curr = fieldParsing.deserializeGameName(curr, data)
                releaseDate, curr = fieldParsing.deserializeVariableLen(curr, data, fieldLen.DATE_LEN)
                
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

                genres, curr = fieldParsing.deserializeVariableLen(curr, data, fieldLen.GENRE_LEN)

                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.GENRE_LEN)
                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.MEDIA_LEN)
                curr = fieldParsing.skipVariableLen(curr, data, fieldLen.MEDIA_LEN)
                
                entries.append(ReducedGameEntry(appID, name, releaseDate, windows, mac, linux, avgPlaytimeForever, genres))
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")
        return entries