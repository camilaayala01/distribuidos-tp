import socket
import os
import threading 

def sendall(msg, addr, sock):
    sent = 0
    while sent < len(msg):
        sent += sock.sendto(msg[sent:], addr)

class HealthcheckAnswerController:
    def __init__(self):
        self._nodeName = os.getenv('NODE_NAME')
        self._running = True
        self._healthcheckPort = int(os.getenv('HEALTHCHECK_PORT')) 
    
    def setUpHealthcheck(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((f'{self._nodeName}', self._healthcheckPort))
        sock.settimeout(2)
        while self._running:
            try:
                data, addr = sock.recvfrom(1024)
                if data.decode('utf-8') == "check":
                    msg = f"ack:{self._nodeName}".encode('utf-8')
                    sendall(msg, addr, sock)
            except TimeoutError:
                continue
        sock.close()
        
    def stop(self, _signum, _frame):
        self._running = False

    def execute(self):
        threading.Thread(target=self.setUpHealthcheck).start()

