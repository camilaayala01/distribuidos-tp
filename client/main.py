import logging
from entryParsing.common.utils import initializeLog
from common.messages import processResponse, serializeAndFragmentWithTable
from common.utils import loadGames, loadReviews
from entryParsing.common.table import Table
from common.client import Client
import signal 

QUERY_COUNT = 5
MAX_DATA_BYTES = 51200   

def main():
    initializeLog()
    client = Client()
    signal.signal(signal.SIGTERM, client.stop)
    serializeAndFragmentWithTable(client, MAX_DATA_BYTES, loadGames, Table.GAMES)
    serializeAndFragmentWithTable(client, MAX_DATA_BYTES, loadReviews, Table.REVIEWS)

    if client.isRunning():
        logging.info(f'action: wait for responses | result: success | msg: finalized data sending')
    queriesFullyAnswered = 0
    while queriesFullyAnswered < QUERY_COUNT and client.isRunning():
        msg = client.receiveFromServer()
        if msg == None:
            continue
        isQueryResolved = processResponse(msg)
        if isQueryResolved:
            queriesFullyAnswered += 1

    client.closeSocket()
    logging.info(f'action: gracefully shutting down | result: success')


if __name__ == "__main__":
    main()