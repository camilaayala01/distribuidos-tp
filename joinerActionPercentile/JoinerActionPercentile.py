import os
from joinerByAppID.common.joinerNameCountByAppID import JoinerNameCountByAppID

"""
Entities that join all entries maintaining total counts for all
game IDs that belong to 'Action' category
More than one entity
Query 5
"""
class JoinerActionNegativeReviewsPercentile(JoinerNameCountByAppID):
    def __init__(self):
        super().__init__(type=os.getenv('JOIN_PERC_NEG_REV'), id=os.getenv('NODE_ID'))

    def _sendToNextStep(self, msg: bytes):
        self._internalComunnication.sendToActionPercentileSorterConsolidator(msg)