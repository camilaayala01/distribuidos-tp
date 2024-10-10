import os
import logging
from entryParsing.common.utils import initializeLog
from internalCommunication.internalCommunication import InternalCommunication
from grouperReviews.common.grouperReviews import GrouperReviews
from entryParsing.common.headerWithSender import HeaderWithSender
from entryParsing.entryAppIDNameReviewCount import EntryAppIDNameReviewCount
from entryParsing.entryAppIDName import EntryAppIDName

"""
Entities that count the amount of reviews in a batch that belong to the same game
grouping them by AppID
They receive batches of negative reviews only and responds with App ID, Name of the Game and review count
More than one entity
Query 4
"""

class GrouperActionEnglishNegativeReviews:
    def __init__(self): 
        initializeLog()
        self._internalCommunication = InternalCommunication(os.getenv('GROUP_ENG_NEG_REV'), os.getenv('NODE_ID'))
    
    def stop(self, _signum, _frame):
        self._internalCommunication.stop()

    def sendToNextStep(self, header, result):
        data = header.serialize()
        for entry in result:
            data += entry.serialize()
        self._internalCommunication.sendToEnglishReviewsJoinerConsolidator(data)

    def _applyStep(self, entries: list['EntryAppIDName'])-> list['EntryAppIDNameReviewCount']:
        return self._buildResult(self._count(entries))
    
    def _count(self, entries: list['EntryAppIDName']) -> dict[str, int]:
        appIDCount = {}
        for entry in entries:
            if not appIDCount.get(entry._appID):
                appIDCount[entry._appID] = EntryAppIDNameReviewCount(entry._appID, entry._name, 1)
            else:
                appIDCount[entry._appID].addToCount(1)
        return appIDCount
    
    def _buildResult(self, appIDCount: dict[str, int]) -> list['EntryAppIDNameReviewCount']:
        result = []
        for value in appIDCount.values():
            result.append(value)
        return result
    
    def execute(self):
        self._internalCommunication.defineMessageHandler(self.handleMessage)
    
    
    def handleMessage(self, ch, method, properties, body):
        header, data = HeaderWithSender.deserialize(body)
        logging.info(f'action: received reviews batch | {header} | result: success')
        entries = EntryAppIDName.deserialize(data)
        result = self._applyStep(entries)
        self.sendToNextStep(header, result)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    