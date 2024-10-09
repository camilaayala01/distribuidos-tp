import zmq

class Client:
    def __init__(self):
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        socket.connect("tcp://border-node:%s" % "5556")
        self._socket = socket
        self._working = True

    def stop(self, _signum, _frame):
        self._working = False

    def closeSocket(self):
        self._socket.close()

    def receiveFromServer(self):
        return self._socket.recv()
    
    def sendToServer(self, msg):
        self._socket.send(msg)

    def isRunning(self):
        return self._working