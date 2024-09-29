from .entryDateFilterer import EntryDateFilterer
from datetime import datetime

class DateFilterer():
    def __init__(self, bottomDate: datetime, topDate: datetime):
        self._bottomDate = bottomDate
        self._topDate = topDate

    def execute(self, data: bytes):
        # communication is not developed
        print("work in progress")

    def filterBatch(self, batch: list[EntryDateFilterer]) -> list[EntryDateFilterer]:
        return [entry for entry in batch if (self._bottomDate <= entry.getDate() and self._topDate >= entry.getDate())]