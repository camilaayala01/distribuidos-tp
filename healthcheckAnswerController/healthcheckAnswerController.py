import socket
import os
import threading

from .messages import HeartbeatMessage 

def sendall(msg, addr, sock):
    sent = 0
    while sent < len(msg):
        sent += sock.sendto(msg[sent:], addr)

class HealthcheckAnswerController:
    def __init__(self):
        self._nodeName = os.getenv('NODE_NAME')
        self._running = True
        self._healthcheckPort = int(os.getenv('HEALTHCHECK_PORT'))
        self._handle = None 
    
    def isRunning(self):
        return self._running
    
    def setUpHealthcheck(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f'escucho en {self._nodeName}')
        sock.bind((f'{self._nodeName}', self._healthcheckPort))
        sock.settimeout(2)
        while self.isRunning(): 
            try:
                data, addr = sock.recvfrom(1024)
                msg, _ = HeartbeatMessage.deserialize(data)    
                if msg == HeartbeatMessage.CHECK:
                    sendall(HeartbeatMessage.ACK.serialize(self._nodeName), addr, sock)
            except TimeoutError:
                continue
        sock.close()
        
    def stop(self):
        print("dejo de correr")
        self._running = False
        if self._handle:
            self._handle.join()

    def execute(self):
        healthcheckThread = threading.Thread(target=self.setUpHealthcheck)
        self._handle = healthcheckThread
        healthcheckThread.start()
        print("levanto el healthcheck y eso gordi")


