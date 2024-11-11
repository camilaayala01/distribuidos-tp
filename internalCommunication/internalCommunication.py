import pika
import os
import logging

PREFETCH_COUNT = 1 # break round robin
DELIVERY_MODE = 1 # make message transient, doesn't matter yet

class InternalCommunication:
    def __init__(self, name: str = None, nodeID: str = None):
        self._executerName = name
        self._connection = self.startConnection()
        self._channel = self.createChannel()
        self._nodeID = nodeID
        if name != None:
            logging.info(f'action: initialized an entity | result: success | msg: binded to queue {name}')

    def startConnection(self) -> pika.BlockingConnection:
        return pika.BlockingConnection(
        pika.ConnectionParameters(host=os.getenv('HOST'), heartbeat=0))

    def createChannel(self) -> pika.adapters.blocking_connection.BlockingChannel:
        channel = self._connection.channel()
        channel.basic_qos(prefetch_count=PREFETCH_COUNT)
        return channel

    def declareExchange(self, exchangeName: str, routingKey: str) -> str:
        self._channel.exchange_declare(exchange=exchangeName, exchange_type='direct')
        result = self._channel.queue_declare(queue='', auto_delete = True)
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
            self._channel.queue_declare(queue=self._executerName, durable=False)
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
        self._channel.queue_declare(queue=queueName)
        self._channel.basic_publish(
            exchange='',
            routing_key= queueName,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode= DELIVERY_MODE, 
            ))
        
    def directSend(self, exchangeName: str, routingKey: str, message: bytes):
        self._channel.exchange_declare(exchange=exchangeName, exchange_type='direct')
        self._channel.basic_publish(exchange=exchangeName, routing_key=routingKey, body=message)

    def sendToInitializer(self, message: bytes):
        self.basicSend(os.getenv('INIT'), message)