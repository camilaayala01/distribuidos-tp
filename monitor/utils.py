import os
import socket

CONTAINER_NAME = os.getenv('CONTAINER_NAME')
MONITOR_COUNT = int(os.getenv('MONITOR_COUNT'))

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
            break
        
def getSocket(id, port, socketTimeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((monitorName(id), port))
    sock.settimeout(socketTimeout)
    return sock

def getServerSocket(id, port, socketTimeout):
    listeningSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listeningSock.bind((monitorName(id), port)) 
    listeningSock.settimeout(socketTimeout)      
    listeningSock.listen(MONITOR_COUNT)
    return listeningSock

def sendto(senderId, port, recvId, msg, timeout):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((monitorName(recvId), port))
        s.sendall(msg.serialize(senderId))
    except:
        return None
    return s



        
