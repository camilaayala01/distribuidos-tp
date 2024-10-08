import os
from entryParsing.entryNameReviewCount import EntryNameReviewCount
from joiner.common.joinerNameCountByAppID import JoinerNameCountByAppID
import logging

"""
Entities that join all entries maintaining total counts for all
game IDs that belong to 'Indie' category
More than one entity
Query 3
"""
class JoinerIndiePositiveReviews(JoinerNameCountByAppID):
    def __init__(self):
        super().__init__(type=os.getenv('JOIN_INDIE_POS_REV'), id=os.getenv('NODE_ID'))

    def _sendToNextStep(self, msg: bytes):
        self._internalCommunication.sendToIndiePositiveReviewsConsolidator(msg)
        logging.info("action: sending joined batch to consolidator | result: success")

    def entriesToSend(self)-> list[EntryNameReviewCount]:
        return self._joinedEntries.values()
        