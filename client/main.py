import zmq
import time
from common.messages import processResponse
from common.utils import loadGames, loadReviews
from entryParsing.common.table import Table
from entryParsing.common.utils import serializeAndFragmentWithTable

QUERY_COUNT = 5
MAX_DATA_BYTES = 8000
port = "5556"

def main():
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect("tcp://border-node:%s" % port)
    print("About to send game table")
    serializeAndFragmentWithTable(socket, MAX_DATA_BYTES, loadGames, Table.GAMES)
    print("About to send review table")
    serializeAndFragmentWithTable(socket, MAX_DATA_BYTES, loadReviews, Table.REVIEWS)

    print("Waiting for responses")
    queriesFullyAnswered = 0
    while queriesFullyAnswered < QUERY_COUNT:
        msg = socket.recv() 
        print(msg)
        isQueryResolved = processResponse(msg)
        if isQueryResolved:
            print("resolved query")
            queriesFullyAnswered += 1


if __name__ == "__main__":
    main()