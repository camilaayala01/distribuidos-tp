from entryParsing.entry import EntryInterface

class EntryAppIDNameGenresReleaseDateAvgPlaytime(EntryInterface):
    def __init__(self, _appID: str, _name: str, _genres: str, _releaseDate: str, _avgPlaytime: int):
        super().__init__(_appID=_appID, _name=_name, _genres=_genres, _releaseDate=_releaseDate, _avgPlaytime=_avgPlaytime)

    def getGenres(self) -> str:
        return self._genres