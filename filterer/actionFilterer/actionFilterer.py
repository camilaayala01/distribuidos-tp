from .entryActionFilterer import EntryActionFilterer

class ActionFilterer():
    def __init__(self):
        self._genre = "Action"

    def execute(self, data: bytes):
        # communication is not developed
        print("work in progress")

    def filterBatch(self, batch: list[EntryActionFilterer]) -> list[EntryActionFilterer]:
        return [entry for entry in batch if self._genre in entry.getGenres()]