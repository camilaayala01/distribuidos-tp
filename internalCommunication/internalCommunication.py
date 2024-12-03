import pika
import os
import logging

from entryParsing.common.fieldParsing import serializeBoolean
from internalCommunication.internalMessageType import InternalMessageType

PREFETCH_COUNT = int(os.getenv('PREFETCH_COUNT'))
DELIVERY_MODE = 2 

class InternalCommunication:
    def __init__(self, name: str = None, nodeID: str = None):
        self._executerName = name
        self._nodeID = nodeID or ''
        self._connection = self.startConnection()
        self._queue = None
        self._channel = self.createChannel()
        if name != None:
            logging.info(f'action: initialized an entity | result: success | msg: binded to queue {name}')

    def getQueueName(self) -> str:
        return self._executerName + self._nodeID

    def startConnection(self) -> pika.BlockingConnection:
        return pika.BlockingConnection(
        pika.ConnectionParameters(host=os.getenv('HOST'), heartbeat=0))

    def createChannel(self) -> pika.adapters.blocking_connection.BlockingChannel:
        channel = self._connection.channel()
        channel.basic_qos(prefetch_count=PREFETCH_COUNT)
        return channel

    def defineMessageHandler(self, callback):
        queueName = self._executerName + self._nodeID
        self._queue = self._channel.queue_declare(queue=queueName, durable=True)
        self._channel.basic_consume(queue=queueName, on_message_callback=callback, auto_ack=False)

        self._channel.start_consuming()
        # try:
        #     self._channel.start_consuming()
        # except OSError:
        #     logging.info(f'action: gracefully shutting down | result: success')
        #     self._channel.close()
        #     self._connection.close()

    def stop(self):
        self._channel.stop_consuming()
    
    def basicSend(self, queueName: str, message: bytes):
        self._channel.queue_declare(queue=queueName, durable=True)
        self._channel.basic_publish(
            exchange='',
            routing_key= queueName,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=DELIVERY_MODE, 
            ))
        
    def directSend(self, queueName: str, routingKey: str, message: bytes):
        self.basicSend(queueName=queueName+routingKey, message=message)

    def sendToInitializer(self, message: bytes):
        self.basicSend(os.getenv('INIT'), message)

    def sendToDispatcher(self, message: bytes):
        self.basicSend(os.getenv('DISP'), message)
    
    def ackAll(self, deliveryTags):
        for tag in deliveryTags:
            self._channel.basic_ack(delivery_tag=tag)

    def requeuePacket(self, tag):
        self._channel.basic_nack(delivery_tag=tag, requeue=True)

    def sendFlushToSelf(self, clientToRemove):
        self._internalCommunication.basicSend(self._internalCommunication.getQueueName(), 
                                              InternalMessageType.CLIENT_FLUSH.serialize() 
                                              + clientToRemove 
                                              + serializeBoolean(False))