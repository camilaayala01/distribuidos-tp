import pika
import os
import logging

PREFETCH_COUNT = int(os.getenv('PREFETCH_COUNT'))
DELIVERY_MODE = 2 

class InternalCommunication:
    def __init__(self, name: str = None, nodeID: str = None):
        self._executerName = name
        self._connection = self.startConnection()
        self._channel = self.createChannel()
        self._nodeID = nodeID if nodeID is not None else ''
        if name != None:
            logging.info(f'action: initialized an entity | result: success | msg: binded to queue {name}')

    def startConnection(self) -> pika.BlockingConnection:
        return pika.BlockingConnection(
        pika.ConnectionParameters(host=os.getenv('HOST'), heartbeat=0))

    def createChannel(self) -> pika.adapters.blocking_connection.BlockingChannel:
        channel = self._connection.channel()
        channel.basic_qos(prefetch_count=PREFETCH_COUNT)
        return channel

    def defineMessageHandler(self, callback):
        queueName = self._executerName + self._nodeID
        self._channel.queue_declare(queue=queueName, durable=True)
        self._channel.basic_consume(queue=queueName, on_message_callback=callback)

        try:
            self._channel.start_consuming()
        except OSError as e:
            print(e)
            logging.info(f'action: gracefully shutting down | result: success')
            self._channel.close()
            self._connection.close()

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
        
    def directSend(self, exchangeName: str, routingKey: str, message: bytes):
        self.basicSend(queueName=exchangeName+routingKey, message=message)

    def sendToInitializer(self, message: bytes):
        self.basicSend(os.getenv('INIT'), message)