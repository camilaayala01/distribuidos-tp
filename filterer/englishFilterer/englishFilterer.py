from .entryEnglishFilterer import EntryEnglishFilterer
from langid import classify

class EnglishFilterer():
    def __init__(self, lang: str):
        self._lang = lang

    def execute(self, data: bytes):
        # communication is not developed
        print("work in progress")

    def filterBatch(self, batch: list[EntryEnglishFilterer]) -> list[EntryEnglishFilterer]:
        return [entry for entry in batch if self._lang == classify(entry.getReviewText())[0]]