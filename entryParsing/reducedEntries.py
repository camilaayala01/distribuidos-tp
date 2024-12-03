from abc import abstractmethod
from .messagePart import MessagePartInterface

class EntryAppID(MessagePartInterface):
    def __init__(self, _appID: str):
        super().__init__(_appID=_appID)


class EntryAppIDName(MessagePartInterface):
    def __init__(self, _appID: str, _name: str):
        super().__init__(_appID=_appID, _name=_name)

    def __str__(self):
        return f'{self._appID},{self._name};\n'

    @classmethod
    def header(cls):
        return "app_id,Name\n"


class EntryName(MessagePartInterface):
    def __init__(self, _name: str):
        super().__init__(_name=_name)
    
    def __str__(self):
        return f'{self._name}'
    
    @classmethod
    def header(cls):
        return "Name\n"


class EntryNameDateAvgPlaytime(MessagePartInterface):
    def __init__(self, _name: str, _releaseDate: str, _avgPlaytime: int):
        super().__init__(_name=_name, _releaseDate=_releaseDate, _avgPlaytime=_avgPlaytime)

    def getDate(self) -> str:
        return self._releaseDate


class EntryAppIDReviewCount(MessagePartInterface):
    def __init__(self, _appID: str, _reviewCount: int):
        super().__init__(_appID=_appID, _reviewCount=_reviewCount)

    def getAppID(self):
        return self._appID
    
    def getCount(self):
        return self._reviewCount
    
    def addToCount(self, count: int):
        self._reviewCount += count


class EntryAppIDReviewText(MessagePartInterface):
    def __init__(self, _appID: str, _reviewText: str):
        super().__init__(_appID=_appID, _reviewText=_reviewText)

    def getAppID(self):
        return self._appID

    def getReviewText(self):
        return self._reviewText


class EntryAppIDNameReviewText(MessagePartInterface):
    def __init__(self, _appID: str, _name: str, _reviewText: str):
        super().__init__(_appID=_appID, _name=_name, _reviewText=_reviewText)

    def getReviewText(self):
        return self._reviewText
    

class EntryAppIDNameGenres(MessagePartInterface):
    def __init__(self, _appID: str, _name: str, _genres: str):
        super().__init__(_appID=_appID, _name=_name, _genres=_genres)

    def getGenres(self) -> str:
        return self._genres
    

class EntryAppIDNameGenresReleaseDateAvgPlaytime(MessagePartInterface):
    def __init__(self, _appID: str, _name: str, _genres: str, _releaseDate: str, _avgPlaytime: int):
        super().__init__(_appID=_appID, _name=_name, _genres=_genres, _releaseDate=_releaseDate, _avgPlaytime=_avgPlaytime)

    def getGenres(self) -> str:
        return self._genres


class EntryOSCount(MessagePartInterface):
    def __init__(self, _windowsCount: int, _macCount: int, _linuxCount: int, _totalCount: int):
        super().__init__(_windowsCount=_windowsCount, _macCount=_macCount, _linuxCount=_linuxCount, _totalCount=_totalCount)

    def getWindowsCount(self):
        return self._windowsCount
    
    def getMacCount(self):
        return self._macCount
    
    def getLinuxCount(self):
        return self._linuxCount

    def getTotalCount(self):
        return self._totalCount

    def sumEntry(self, entry: 'EntryOSCount'):
        self._windowsCount += entry.getWindowsCount()
        self._macCount += entry.getMacCount()
        self._linuxCount += entry.getLinuxCount()
        self._totalCount += entry.getTotalCount()

    def __str__(self):
        return f"Total de juegos: {str(self._totalCount)}\nTotal de juegos soportados en Windows: {str(self._windowsCount)}\nTotal de juegos soportados en Linux: {str(self._linuxCount)}\nTotal de juegos soportados en Mac: {str(self._macCount)}"
    

class EntryOSSupport(MessagePartInterface):
    def __init__(self, _windows: int, _mac: int, _linux: int):
        super().__init__(_windows=_windows, _mac=_mac, _linux=_linux)
        

# entries for sorters: contain sorting functions
class EntrySorterTopFinder(MessagePartInterface):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def isGreaterThanOrEqual(self, otherEntry: 'EntrySorterTopFinder') -> bool:
        return self.getSortingAtribute() >= otherEntry.getSortingAtribute()
    
    @abstractmethod
    def getSortingAtribute(self) -> int:
        pass

    @classmethod
    def sort(cls, entries: list['EntrySorterTopFinder'], reversed: bool) -> list['EntrySorterTopFinder']:
        return sorted(entries, key=lambda entry: entry.getSortingAtribute(), reverse=reversed)
    

class EntryAppIDNameReviewCount(EntrySorterTopFinder):
    def __init__(self, _appID: str, _name: str, _reviewCount: int):
        super().__init__(_appID=_appID, _name=_name, _reviewCount=_reviewCount)

    def getAppID(self):
        return self._appID
    
    def getName(self):
        return self._name
    
    def getCount(self):
        return self._reviewCount
          
    def addToCount(self, count: int):
        self._reviewCount += count
    
    def getSortingAtribute(self) -> int:
        return self._reviewCount
    

class EntryNameAvgPlaytime(EntrySorterTopFinder):
    def __init__(self, _name: str, _avgPlaytime: int):
        super().__init__(_name=_name, _avgPlaytime=_avgPlaytime)  

    def __str__(self):
        return f"{self._name},{self._avgPlaytime};"
    
    def csv(self):
        return f"{self._name},{self._avgPlaytime}\n"

    @classmethod
    def header(self):
        return f"Name,Average playtime forever\n"
    
    def getSortingAtribute(self) -> int:
        return self._avgPlaytime
    
    @classmethod
    def sort(cls, entries: list['EntrySorterTopFinder'], reversed: bool) -> list['EntrySorterTopFinder']:
        return super().sort(entries, reversed)
    

class EntryNameReviewCount(EntrySorterTopFinder):
    def __init__(self, _name: str, _reviewCount: int):
        super().__init__(_name=_name, _reviewCount=_reviewCount)

    def getName(self):
        return self._name
    
    def getCount(self):
        return self._reviewCount
    
    def addToCount(self, count: int):
        self._reviewCount += count

    @classmethod
    def header(cls):
        return("Name,positive_score\n")

    def __str__(self):
        return f"{self._name},{self._reviewCount};"
    
    def getSortingAtribute(self) -> int:
        return self._reviewCount
