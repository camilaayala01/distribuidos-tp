class Query1Response:
    def __init__(self, windowsCount: int, macCount: int, linuxCount: int):
        self.windowsCount = windowsCount
        self.macCount = macCount
        self.linuxCount = linuxCount
class GamesNamesResponse:
    def __init__(self, results: list[str]):
        self.gamesNames = results
class Query2Response(GamesNamesResponse):
    def __init__(self, topAvgTimeIndie2010sGamesNames: list[str]):
        super().__init__(topAvgTimeIndie2010sGamesNames)
class Query3Response(GamesNamesResponse):
    def __init__(self, topPosRevIndieGamesNames: list[str]):
        super().__init__(topPosRevIndieGamesNames)
class Query4Response(GamesNamesResponse):
    def __init__(self, topPosRevActionGamesNames: list[str]):
        super().__init__(topPosRevActionGamesNames)
class Query5Response(GamesNamesResponse):
    def __init__(self, topNegRevActionGamesNames: list[str]):
        super().__init__(topNegRevActionGamesNames)
