import logging
from common.client import Client
from entryParsing.common.utils import initializeLog
from common.utils import loadGames, loadReviews
from entryParsing.common.table import Table
import signal 
import time
import os

QUERY_COUNT = 5

def main():
    initializeLog()
    client = Client()
    signal.signal(signal.SIGTERM, client.stopWorking)

    for _ in range(client._amountOfExecutions):
        logging.info(f'action: starting execution number {client._currentExecution} | result: success')
        client.sendTables(loadGames, loadReviews)
        if client.isRunning():
            logging.info(f'action: wait for responses | result: success | msg: finalized data sending')
            client.waitForResponses()
        else: 
            break
        
        if not client.isLastExecution():
            client.reset()

    logging.info(f'action: gracefully shutting down | result: success')
    client.shutdown()

if __name__ == "__main__":
    main()