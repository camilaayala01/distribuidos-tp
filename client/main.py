import zmq
import logging
from common.messages import processResponse
from common.utils import loadGames, loadReviews
from entryParsing.common.table import Table
from entryParsing.common.utils import serializeAndFragmentWithTable
from entryParsing.common.utils import initializeLog

QUERY_COUNT = 5
MAX_DATA_BYTES = 8000
port = "5556"    

def main():
    initializeLog()
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect("tcp://border-node:%s" % port)
    serializeAndFragmentWithTable(socket, MAX_DATA_BYTES, loadGames, Table.GAMES)
    serializeAndFragmentWithTable(socket, MAX_DATA_BYTES, loadReviews, Table.REVIEWS)

    logging.info(f'action: wait for responses | result: success | msg: finalized data sending')
    queriesFullyAnswered = 0
    while queriesFullyAnswered < QUERY_COUNT:
        msg = socket.recv()
        isQueryResolved = processResponse(msg)
        if isQueryResolved:
            queriesFullyAnswered += 1


if __name__ == "__main__":
    main()