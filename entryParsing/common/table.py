from enum import Enum

class Table(Enum):
    GAMES = 0
    REVIEWS = 1

    def __str__(self):
        if self == Table.GAMES:
            return "Games"
        elif self == Table.REVIEWS:
            return "Reviews"