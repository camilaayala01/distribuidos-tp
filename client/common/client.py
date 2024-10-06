import zmq
import time

from client.common.messages import processResponse
from client.common.utils import loadGames, loadReviews
from entryParsing.common.table import Table
from entryParsing.common.utils import serializeAndFragmentWithTable

QUERY_COUNT = 5
MAX_DATA_BYTES = 8000
port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://server:%s" % port)

serializeAndFragmentWithTable(socket, MAX_DATA_BYTES, loadGames, Table.GAMES)
serializeAndFragmentWithTable(socket, MAX_DATA_BYTES, loadReviews, Table.REVIEWS)

queriesFullyAnswered = 0
while queriesFullyAnswered < QUERY_COUNT:
    msg = socket.recv() 
    isQueryResolved = processResponse(msg)
    if isQueryResolved:
        queriesFullyAnswered += 1

    
