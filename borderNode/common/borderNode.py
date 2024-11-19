import os
import shutil
from typing import Any, Dict
import uuid

import zmq
from zmq.utils.monitor import recv_monitor_message
from entryParsing.common.fieldParsing import getClientIdUUID
from entryParsing.common.messageType import MessageType
from entryParsing.common.utils import copyFile
from .borderCommunication import BorderNodeCommunication

# do heartbeat when receiving a disconnect event and also when booting (or rebooting)
# what happens if border node fails after receiving a zmq message, before sending it to initializer?
# option 1: implement stop and wait mechanism
# option 2: change queues to rabbit, using subscriptions (exchange) for acks and responses, 
# and queue for data transfer
class BorderNode: 
    def __init__(self):
        self._communication = BorderNodeCommunication()
        self._storagePath = os.getenv('STORAGE_PATH')
        os.makedirs(self._storagePath, exist_ok=True)
        self._activeClients = set() # some in memory lock
        # some file lock for writing clients in log

    def activeClientsFile(self):
        return self._storagePath + 'activeClients'
    
    def stop(self, _signum, _):
        self._communication.stop()
        datafile = self.activeClientsFile() + self.storageFileExtension()
        if os.path.exists(datafile):
            os.remove(datafile)

    def storeNewClient(self, clientId: bytes):
        # managable in-memory size. for 100.000 concurrent clients, uses 1.5MB
        self._activeClients.add(clientId)
        self.storeInDisk(clientId)

    def storageFileExtension(self):
        return '.txt'
    
    def storeInDisk(self, clientId: bytes):
        storageFilePath = self.activeClientsFile()
        with open(storageFilePath + '.tmp', 'w+') as newResults:
            copyFile(newResults, storageFilePath + self.storageFileExtension())
            newResults.write(f"{getClientIdUUID(clientId)}")
        os.rename(storageFilePath + '.tmp', storageFilePath + self.storageFileExtension())

    def handleClientMessage(self, clientId: bytes, data: bytes):
        try:
            type, msg = MessageType.deserialize(data)
        except:
            # wont happen unless client is corrupt
            self._communication.sendToClient(clientId=clientId, data=MessageType.FORMAT_ERROR.serialize())
            return
        
        match type:
            case MessageType.CONNECT:
                assignedId = uuid.uuid4().bytes
                self.storeNewClient(assignedId)
                # if fails exactly here, even tho client will be registered, it will be discarted 
                # within the first heartbeat cycle
                self._communication.sendToClient(clientId, assignedId)
                return None
            case MessageType.DATA_TRANSFER:
                if clientId not in self._activeClients:
                    # wont happen unless client is an attacker
                    self._communication.sendToClient(clientId=clientId, data=MessageType.CONNECT_RETRY.serialize())
                    return None
                return clientId + msg

    def listenForClient(self):
        while self._communication.isRunning():
            received = self._communication.receiveFromClient()
            if received is None:
                continue
            id, data = received
            toSend = self.handleClientMessage(id, data)
            if toSend is not None:
                self._communication.sendInitializer(toSend)
        self._communication.closeClientSocket()

    def runHeartbeat(self):
        # TODO
        print("heartbeat not implemented!")

    def monitor_events(self):
        monitor = self._communication.getMonitorSocket()
        EVENT_MAP = {}
        for name in dir(zmq):
            if name.startswith('EVENT_'):
                value = getattr(zmq, name)
                EVENT_MAP[value] = name

        while monitor.poll():
            evt: Dict[str, Any] = {}
            mon_evt = recv_monitor_message(monitor)
            evt.update(mon_evt)
            evt['description'] = EVENT_MAP[evt['event']]
            if evt['event'] == zmq.EVENT_DISCONNECTED:
                self.runHeartbeat()
            if evt['event'] == zmq.EVENT_MONITOR_STOPPED:
                break
        monitor.close()

    def dispatchResponses(self):
        self._communication.executeDispatcher()