from .common import fieldParsing, fieldLen

SERIALIZERS = {
    # game or review entry
    "_appID": fieldParsing.serializeAppID,
    "_name": fieldParsing.serializeGameName,
    "_releaseDate": fieldParsing.serializeReleaseDate,
    "_estimatedOwners": lambda x: fieldParsing.serializeVariableLen(x, fieldLen.EST_OWN_LEN),
    "_peakCCU": lambda x: fieldParsing.serializeNumber(x, fieldLen.PEAK_CCU_BYTES),
    "_reqAge": lambda x: fieldParsing.serializeNumber(x, fieldLen.REQ_AGE_BYTES),
    "_price": lambda x: fieldParsing.serializeNumber(fieldParsing.floatToInt(x), fieldLen.PRICE_BYTES),
    "_discCount": lambda x: fieldParsing.serializeNumber(x, fieldLen.DISC_COUNT_BYTES),
    "_about": lambda x: fieldParsing.serializeVariableLen(x, fieldLen.ABOUT_LEN),
    "_supLang": lambda x: fieldParsing.serializeVariableLen(x, fieldLen.LANG_LEN),
    "_audioLang": lambda x: fieldParsing.serializeVariableLen(x, fieldLen.LANG_LEN),
    "_reviews": fieldParsing.serializeReviewText,
    "_headerImg": lambda x: fieldParsing.serializeVariableLen(x, fieldLen.MEDIA_LEN),
    "_website": lambda x: fieldParsing.serializeVariableLen(x, fieldLen.URL_LEN),
    "_supportUrl": lambda x: fieldParsing.serializeVariableLen(x, fieldLen.URL_LEN),
    "_supportEmail": lambda x: fieldParsing.serializeVariableLen(x, fieldLen.URL_LEN),
    "_windows": lambda x: fieldParsing.serializeNumber(x, fieldLen.BOOLEAN_LEN),
    "_mac": lambda x: fieldParsing.serializeNumber(x, fieldLen.BOOLEAN_LEN),
    "_linux": lambda x: fieldParsing.serializeNumber(x, fieldLen.BOOLEAN_LEN),
    "_metaScore": lambda x: fieldParsing.serializeNumber(x, fieldLen.META_SCORE_BYTES),
    "_metaUrl": lambda x: fieldParsing.serializeVariableLen(x, fieldLen.URL_LEN),
    "_userScore": lambda x: fieldParsing.serializeNumber(x, fieldLen.USER_SCORE_BYTES),
    "_positive": lambda x: fieldParsing.serializeNumber(x, fieldLen.POSITIVE_BYTES),
    "_negative": lambda x: fieldParsing.serializeNumber(x, fieldLen.NEGATIVE_BYTES),
    "_scoreRank": lambda x: fieldParsing.serializeNumber(fieldParsing.floatToInt(x), fieldLen.SCORE_RANK_BYTES),
    "_achievements": lambda x: fieldParsing.serializeNumber(x, fieldLen.ACHIVEMENT_BYTES),
    "_recs": lambda x: fieldParsing.serializeNumber(x, fieldLen.RECS_BYTES),
    "_notes": lambda x: fieldParsing.serializeVariableLen(x, fieldLen.NOTES_LEN),
    "_avgPlaytime": fieldParsing.serializePlaytime,
    "_avgPlaytimeTwoWeeks": fieldParsing.serializePlaytime,
    "_medianPlaytimeForever": lambda x: fieldParsing.serializeNumber(x, fieldLen.MEDIAN_BYTES),
    "_medianPlaytimeTwoWeeks": lambda x: fieldParsing.serializeNumber(x, fieldLen.MEDIAN_BYTES),
    "_devs": lambda x: fieldParsing.serializeVariableLen(x, fieldLen.TEAM_LEN),
    "_pubs": lambda x: fieldParsing.serializeVariableLen(x, fieldLen.TEAM_LEN),
    "_categories": lambda x: fieldParsing.serializeVariableLen(x, fieldLen.GENRE_LEN),
    "_genres": fieldParsing.serializeGenres,
    "_tags": lambda x: fieldParsing.serializeVariableLen(x, fieldLen.GENRE_LEN),
    "_screens": lambda x: fieldParsing.serializeVariableLen(x, fieldLen.MEDIA_LEN),
    "_movies": lambda x: fieldParsing.serializeVariableLen(x, fieldLen.MEDIA_LEN),
    "_reviewCount": fieldParsing.serializeCount,
    "_windowsCount": fieldParsing.serializeCount,
    "_macCount":  fieldParsing.serializeCount,
    "_linuxCount": fieldParsing.serializeCount, 
    "_totalCount":  fieldParsing.serializeCount,
    "_reviewText": fieldParsing.serializeReviewText,
    "_reviewScore": fieldParsing.serializeSignedInt,
    "_reviewVotes": lambda x: fieldParsing.serializeNumber(x, fieldLen.VOTE_LEN),
    # header
    "_fragment": fieldParsing.serializeCount,
    "_eof": fieldParsing.serializeBoolean,
    "_clientId": lambda x: x,
    "_table": fieldParsing.serializeTable,
    "_sender": fieldParsing.serializeSenderID,
    "_queryNumber": fieldParsing.serializeQueryNumber
}

DESERIALIZERS = {
    # game or review entry
    "_appID": fieldParsing.deserializeAppID,
    "_name": fieldParsing.deserializeGameName,
    "_releaseDate": fieldParsing.deserializeReleaseDate,
    "_reviewText": fieldParsing.deserializeReviewText,
    "_reviewCount":  fieldParsing.deserializeCount,
    "_reviewScore": fieldParsing.deserializeSignedInt,
    "_reviewVotes": lambda curr, data: fieldParsing.deserializeNumber(curr, data, fieldLen.VOTE_LEN),
    "_windows": fieldParsing.deserializeBoolean,
    "_mac": fieldParsing.deserializeBoolean,
    "_linux": fieldParsing.deserializeBoolean,
    "_avgPlaytime": fieldParsing.deserializePlaytime,
    "_genres": fieldParsing.deserializeGenres,
    "_windowsCount": fieldParsing.deserializeCount,
    "_macCount":  fieldParsing.deserializeCount,
    "_linuxCount": fieldParsing.deserializeCount, 
    "_totalCount": fieldParsing.deserializeCount,
    # header
    "_fragment": fieldParsing.deserializeCount,
    "_eof": fieldParsing.deserializeBoolean,
    "_clientId": fieldParsing.getClientID,
    "_table": fieldParsing.deserializeTable,
    "_sender": fieldParsing.deserializeSenderID,
    "_queryNumber": fieldParsing.deserializeQueryNumber
}