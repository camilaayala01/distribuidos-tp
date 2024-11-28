import os
import socket

MSG_FREQ =int(os.getenv('MESSAGE_FREQ'))
CONTAINER_NAME = os.getenv('CONTAINER_NAME')
TIMEOUT = int(os.getenv('TIMEOUT'))

def monitorName(id):
    return f'monitor-{id}'
    
def container(node):
    return f'{CONTAINER_NAME}-{node}-1'

def sendall(msg, addr, sock):
    sent = 0
    while sent < len(msg):
        try:
            sent += sock.sendto(msg[sent:], addr)
        except Exception as e:
            print(e)
            break
        
def getSocket(id, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((monitorName(id), port))
    sock.settimeout(2 * MSG_FREQ)
    return sock
        
