from grouperPositiveReviews.common.entryAppID import EntryAppID

class GrouperPositiveReviews:
    def __init__(self): # for testing purposes
        self._type = "GrouperPositiveReviews"

    def handleMessage(ch, method, properties, body):
        entries = EntryAppID.deserialize(body)
        result = ch.count(entries)

    def execute(self, data: bytes):
        print("work in progress")

    def count(self, entries: list['EntryAppID']) -> dict[str, int]:
        appIDCount = {}
        for entry in entries:
            if not appIDCount.get(entry._appID):
                appIDCount[entry._appID] = 1
            else:
                appIDCount[entry._appID] = appIDCount[entry._appID] + 1
        return appIDCount
   