import zmq
import time

from client.common.messages import buildGameTableMessage, buildReviewTableMessage, sendTable

QUERY_COUNT = 5
port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://server:%s" % port)

sendTable(socket, buildGameTableMessage)
sendTable(socket, buildReviewTableMessage)

queriesFullyAnswered = 0
while end != True:
    msg = socket.recv() 
    print(msg)
    
    # Streams in ZMQ are received as bytes. 
    # Cast the msg to string and decode it to be able to do the comparison
    if msg.decode() == "END":
        end = True
    time.sleep(1)
