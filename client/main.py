import logging
from common.client import Client
from entryParsing.common.utils import initializeLog
from common.utils import loadGames, loadReviews
from entryParsing.common.table import Table
import signal 
import time
import os

QUERY_COUNT = 5
MAX_DATA_BYTES = 51200   

def main():
    initializeLog()
    client = Client()
    signal.signal(signal.SIGTERM, client.stopWorking)
    
    for i in range(int(os.getenv("AMOUNT_OF_EXECUTIONS"))):
        logging.info(f'action: starting execution number {i + 1} | result: success')
        
        client.sendTable(loadGames, Table.GAMES)
        client.sendTable(loadReviews, Table.REVIEWS)

        if client.isRunning():
            logging.info(f'action: wait for responses | result: success | msg: finalized data sending')
            client.waitForResponses()
        else: 
            break

        client.reset()
        time.sleep(0.5)

    logging.info(f'action: gracefully shutting down | result: success')
    client.shutdown()

if __name__ == "__main__":
    main()