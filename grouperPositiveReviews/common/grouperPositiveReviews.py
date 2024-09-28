from entryParsing.common.entryAppID import EntryAppID
import os
class GrouperPositiveReviews:
    def __init__(self): # for testing purposes
        self._type = os.getenv('GROUP_POS_REV')

    def handleMessage(self, ch, method, properties, body):
        entries = EntryAppID.deserialize(body)
        result = self.count(entries)
        print(result)

    def execute(self, data: bytes):
        print("work in progress")

    def count(self, entries):
        appIDCount = {}
        for entry in entries:
            if not appIDCount.get(entry._appID):
                appIDCount[entry._appID] = 1
            else:
                appIDCount[entry._appID] = appIDCount[entry._appID] + 1
        return appIDCount
   