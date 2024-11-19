from typing import Any, Dict
import uuid

import zmq
from zmq.utils.monitor import recv_monitor_message
from entryParsing.common.messageType import MessageType
from .borderCommunication import BorderNodeCommunication

# do heartbeat when receiving a disconnect event and also when booting (or rebooting)
class BorderNode: 
    def __init__(self):
        self._communication = BorderNodeCommunication()
        self._activeClients = set() # some in memory lock
        # some file lock for writing clients in log

    def stop(self, _signum, _):
        self._communication.stop()
        # delete active clients data

    def handleClientMessage(self, clientId: bytes, data: bytes):
        type, msg = MessageType.deserialize(data)
        match type:
            case MessageType.CONNECT:
                assignedId = uuid.uuid4().bytes
                # write in file
                # in case of failure at this point, client should re-try handshake
                self._activeClients.add(assignedId)
                self._communication.sendToClient(clientId, assignedId)
                
                return None
            case MessageType.DATA_TRANSFER:
                # avoid ddos receiving messages from non registered clients
                if clientId not in self._activeClients:
                    # por las dudas, deberia mandar un mensaje al initializer para q flushee
                    # y uno al cliente para q se registre
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
                print(evt)
            if evt['event'] == zmq.EVENT_MONITOR_STOPPED:
                break
        monitor.close()

    def dispatchResponses(self):
        self._communication.executeDispatcher()