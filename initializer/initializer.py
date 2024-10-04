from ..internalCommunication.internalComunication import InternalCommunication
import os

class Initializer:
    def __init__(self): 
        self._internalCommunication = InternalCommunication(os.getenv('INIT'), os.getenv('NODE_ID'))

    def handleMessage(self, ch, method, properties, body):
        #QUERY 1
        message = bytes()
        # DO SMTH
        self._internalCommunication.sendToOSCountsGrouper(message)

        #QUERY 2
        message = bytes()
        # DO SMTH
        self._internalCommunication.sendToIndieFilter(message)

        #QUERY 3
        message = bytes()
        # DO SMTH
        self._internalCommunication.sendToPositiveReviewsGrouper(message)

        #QUERY 4 AND 5
        message = bytes()
        # DO SMTH
        self._internalCommunication.sendToActionFilter(message)

        message = bytes()   
        # DO SMTH
        self._internalCommunication.sendToNegativeReviewsGrouper(message)

        message = bytes()   
        # DO SMTH
        self._internalCommunication.sendToPositiveReviewsActionGamesJoiner(message)


        return


    def execute(self):
        self._internalComunnication.defineMessageHandler(self.handleMessage)