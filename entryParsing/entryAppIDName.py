from entryParsing.entry import EntryInterface

class EntryAppIDName(EntryInterface):
    def __init__(self, _appID: str, _name: str):
        super().__init__(_appID=_appID, _name=_name)

    def __str__(self):
        return f'{self._appID},{self._name};\n'

    @classmethod
    def header(cls):
        return "app_id,Name\n"
    