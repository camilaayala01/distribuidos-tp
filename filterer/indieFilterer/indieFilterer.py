from .entryIndieFilterer import EntryIndieFilterer

class FiltererIndie():
    def __init__(self):
        self._genre = "Indie"

    def execute(self, data: bytes):
        # communication is not developed
        print("work in progress")

    def filterBatch(self, batch: list[EntryIndieFilterer]) -> list[EntryIndieFilterer]:
        return [entry for entry in batch if self._genre in entry.getGenres()]