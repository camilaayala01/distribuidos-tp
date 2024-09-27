# amount of bytes dedicated to stating the length of the name
NAME_LEN = 1 
AVG_PLAYTIME_LEN = 4

class EntryNameAvgPlaytime:
    def __init__(self, name: str, avgPlaytime: int):
        self._name = name
        self._avgPlaytime = avgPlaytime

    def serialize(self) -> bytes:
        nameBytes = self._name.encode()
        nameLenByte = len(nameBytes).to_bytes(NAME_LEN, 'big')
        avgPlaytimeBytes = self._avgPlaytime.to_bytes(AVG_PLAYTIME_LEN, 'big')

        return nameLenByte + nameBytes + avgPlaytimeBytes  

    def __str__(self):
        return f"EntryNameAvgPlaytime(name={self._name}, avgPlaytime={self._avgPlaytime})"
    
    @staticmethod
    def deserialize(data: bytes) -> list['EntryNameAvgPlaytime']:
        curr = 0
        entries = []

        while len(data) > curr:
            try:
                nameLen = int.from_bytes(data[curr:curr+NAME_LEN], 'big')
                curr+=NAME_LEN
                name = data[curr:nameLen+curr].decode()
                curr += nameLen
                avgPlaytime = int.from_bytes(data[curr:curr+AVG_PLAYTIME_LEN], 'big')
                curr+= AVG_PLAYTIME_LEN

                entries.append(EntryNameAvgPlaytime(name, avgPlaytime))
            except (IndexError, UnicodeDecodeError):
                raise Exception("There was an error parsing data")

        return entries

    def isGreaterThan(self, otherEntry: 'EntryNameAvgPlaytime'):
        return self._avgPlaytime > otherEntry._avgPlaytime
    
    @staticmethod
    def sort(entries: list['EntryNameAvgPlaytime']) -> list['EntryNameAvgPlaytime']:
        return sorted(entries, key=lambda entry: entry._avgPlaytime, reverse=True)