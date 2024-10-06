import pika
import signal
import os
from internalCommunication.internalCommunication import InternalCommunication
import zmq
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber

PREFETCH_COUNT = 1 # break round robin
DELIVERY_MODE = 1 # make message transient, es lo mismo por ahora

class BorderNodeCommunication:
    def __init__(self):
        self._connection = self.startConnection()
        self._channel = self.createChannel()
        self._clientSocket = zmq.Context().socket(zmq.PAIR)
        self._clientSocket.bind("tcp://*:%s" % "5556")
        self._internalCommunication = InternalCommunication(os.getenv('RESP_DISP'), os.getenv('NODE_ID'))
        self._internalCommunication.defineMessageHandler(self.sendClient)

    def startConnection(self) -> pika.BlockingConnection:
        signal.signal(signal.SIGTERM, self.stop)
        return pika.BlockingConnection(
        pika.ConnectionParameters(host=os.getenv('HOST')))

    def createChannel(self) -> pika.adapters.blocking_connection.BlockingChannel:
        channel = self._connection.channel()
        channel.basic_qos(prefetch_count=PREFETCH_COUNT)
        return channel

    def declareExchange(self, exchangeName: str, routingKey: str) -> str:
        self._channel.exchange_declare(exchange=exchangeName, exchange_type='direct')
        result = self._channel.queue_declare(queue='', durable=True)
        queueName = result.method.queue
        self._channel.queue_bind(
                exchange=exchangeName, queue=queueName, routing_key=routingKey)
        return queueName

    def defineMessageHandler(self, callback):
        queueName = ""
        if self._nodeID:
            queueName = self.declareExchange(self._executerName, self._nodeID)
        else:
            queueName = self._executerName
            self._channel.queue_declare(queue=self._executerName)
        self._channel.basic_consume(queue=queueName, on_message_callback=callback)
        try:
            self._channel.start_consuming() 
        # Don't recover connections closed by server
        except pika.exceptions.ConnectionClosedByBroker:
            pass
    
    def readFromQueue(self):
        return self._channel.basic.get(self._executerName)[2]

    def stop(self):
        self._connection.close()

    def basicSend(self, queueName: str, message: bytes):
        self._channel.queue_declare(queue=queueName)
        self._channel.basic_publish(
            exchange='',
            routing_key= queueName,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode= DELIVERY_MODE, 
            ))
        
    def receiveFromClient(self):
        return self._clientSocket.recv()
    
    def sendClient(self, ch, method, properties, body):
        self._clientSocket.send(body)

    def sendInitializer(self, message: bytes):
        self.basicSend(os.getenv('INIT'), message)
 