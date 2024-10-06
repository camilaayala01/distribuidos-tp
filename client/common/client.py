import zmq
import time

from common.messages import buildGameTableMessage, buildReviewTableMessage, processResponse, sendTable

QUERY_COUNT = 5
port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://server:%s" % port)

sendTable(socket, buildGameTableMessage)
sendTable(socket, buildReviewTableMessage)

queriesFullyAnswered = 0
while queriesFullyAnswered < QUERY_COUNT:
    msg = socket.recv() 
    isQueryResolved = processResponse(msg)
    if isQueryResolved:
        queriesFullyAnswered += 1
    
