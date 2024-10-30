import logging
from common.client import Client
from entryParsing.common.utils import initializeLog
from common.utils import loadGames, loadReviews
from entryParsing.common.table import Table
import signal 

QUERY_COUNT = 5
MAX_DATA_BYTES = 51200   

def main():
    initializeLog()
    client = Client()
    signal.signal(signal.SIGTERM, client.stopWorking)
    client.sendTable(loadGames, Table.GAMES)
    client.sendTable(loadReviews, Table.REVIEWS)

    if client.isRunning():
        logging.info(f'action: wait for responses | result: success | msg: finalized data sending')
        client.waitForResponses()

    client.shutdown()
    logging.info(f'action: gracefully shutting down | result: success')


if __name__ == "__main__":
    main()