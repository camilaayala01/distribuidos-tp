import zmq
import time


port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://server:%s" % port)

for i in range(10):
    socket.send(str.encode("client message to server: {}".format(i)))

print("Stopping Client with ZMQ.PAIR socket")
socket.send(b"END")
end = False
while end != True:
    msg = socket.recv() 
    print(msg)

    # Streams in ZMQ are received as bytes. 
    # Cast the msg to string and decode it to be able to do the comparison
    if msg.decode() == "END":
        end = True
    time.sleep(1)
