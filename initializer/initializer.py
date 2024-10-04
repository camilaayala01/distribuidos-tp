from ..internalCommunication.internalCommunication import InternalCommunication
from ..entryParsing.common.headerWithTable import HeaderWithTable
from ..entryParsing.gameEntry import GameEntry
from ..entryParsing.reviewEntry import ReviewEntry
import os

class Initializer:
    def __init__(self): 
        self._internalCommunication = InternalCommunication(os.getenv('INIT'), os.getenv('NODE_ID'))

    def handleMessage(self, ch, method, properties, body):
        header, data = HeaderWithTable.deserialize(body)
        serializedHeader = header.serialize()

        if header.isGamesTable():
            gameEntries = GameEntry.deserialize(data)

            entriesQuery1 = [entry.serializeForQuery1() for entry in gameEntries].sum()

            self._internalCommunication.sendToOSCountsGrouper(serializedHeader + entriesQuery1)
            
            entriesQuery2And3 = [entry.serializeForQuery2And3() for entry in gameEntries].sum()
            self._internalCommunication.sendToIndieFilter(serializedHeader + entriesQuery2And3)

            entriesQuery4And5 = [entry.serializeForQuery4And5() for entry in gameEntries].sum()
            self._internalCommunication.sendToActionFilter(serializedHeader + entriesQuery4And5)
            
        elif header.isReviewsTable():
            reviewEntries = ReviewEntry.deserialize(data)
            positiveReviewEntries = [entry for entry in reviewEntries if entry.isPositive()]
            negativeReviewEntries = [entry for entry in reviewEntries if not entry.isPositive()]

            entriesQuery3 = [entry.serializeForQuery3And5() for entry in positiveReviewEntries].sum()
            self._internalCommunication.sendToPositiveReviewsGrouper(entriesQuery3)

            nodeCount = int(os.getenv('JOIN_ACT_POS_REV_COUNT'))
            shardedResults = ReviewEntry.shardBatch(nodeCount, positiveReviewEntries)
            for i in range(nodeCount):
                self._internalCommunication.sendToPositiveReviewsActionGamesJoiner(str(i), serializedHeader + shardedResults[i])
 
            entriesQuery5 = [entry.serializeForQuery3And5() for entry in negativeReviewEntries].sum()
            self._internalCommunication.sendToNegativeReviewsGrouper(entriesQuery5)

            return
        
        else:
            raise ValueError()

        message = bytes()   
        # DO SMTH
        self._internalCommunication.sendToPositiveReviewsActionGamesJoiner(message)


        return


    def execute(self):
        self._internalComunnication.defineMessageHandler(self.handleMessage)