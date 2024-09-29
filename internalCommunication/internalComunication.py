import pika
import signal
import os
PREFETCH_COUNT = 1 # break round robin
DELIVERY_MODE = 1 # make message transient, es lo mismo por ahora
class InternalCommunication:
    def __init__(self, name: str, nodeID: str = None):
        self._executerName = name
        self._connection = self.startConnection()
        self._channel = self.createChannel()
        self._nodeID = nodeID

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
    
    def readFromQueue(self) :
        # basic.get return type is a three-tuple; (None, None, None) if the queue was empty; otherwise (method, properties, body); NOTE: body may be None
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
        
    
    def fanoutSend(self, exchangeName: str, message: bytes):
        self._channel.exchange_declare(exchange=exchangeName, exchange_type='fanout')
        self._channel.basic_publish(exchange=exchangeName, routing_key='', body=message)


    def directSend(self, exchangeName: str, routingKey: str, message: bytes):
        self._channel.exchange_declare(exchange=exchangeName, exchange_type='direct')
        self._channel.basic_publish(exchange=exchangeName, routing_key=routingKey, body=message)


    def sendToActionFilter(self, message: bytes):
        self.basicSend(os.getenv('FILT_ACT'), message)
    
    def sendToIndieFilter(self, message: bytes):
        self.basicSend(os.getenv('FILT_INDIE'), message)

    def sendToDecadeFilter(self, message: bytes):
        self.basicSend(os.getenv('FILT_DEC'), message)
    
    def sentToEnglishFilter(self, message: bytes):
        self.basicSend(os.getenv('FILT_ENG'), message)
        
    def sendToPositiveReviewsGrouper(self, message: bytes):
        self.basicSend(os.getenv('GROUP_POS_REV'), message)

    def sendToNegativeReviewsGrouper(self, message: bytes):
        self.basicSend(os.getenv('GROUP_NEG_REV'), message)

    def sendToOSCountsGrouper(self, message: bytes):
        self.basicSend(os.getenv('GROUP_OS'), message)
        
    def sendToOSCountsJoiner(self, shardingKey: str, message: bytes):
        self.directSend(os.getenv('JOIN_OS'), shardingKey, message)
    def sendOSCountsJoinEOF(self, message: bytes):
        self.fanoutSend(os.getenv('JOIN_OS'), message)
    
    def sendToPositiveReviewsActionGamesJoiner(self, shardingKey: str, message: bytes):
        self.directSend(os.getenv('JOIN_ACT_POS_REV'), shardingKey, message)
    def sendPositiveReviewsActionGamesJoinEOF(self, message: bytes):
        self.fanoutSend(os.getenv('JOIN_ACT_POS_REV'), message)

    def sendToNegativeReviewsActionGamesJoiner(self, shardingKey: str, message: bytes):
        self.directSend(os.getenv('JOIN_ACT_NEG_REV'), shardingKey, message)
    def sendNegativeReviewsActionGamesJoinEOF(self, message: bytes):
        self.fanoutSend(os.getenv('JOIN_ACT_NEG_REV'), message)


    def sendToReviewsIndieGamesJoiner(self, shardingKey: str, message: bytes):
        self.directSend(os.getenv('JOIN_INDIE_REV'), shardingKey, message)
    def sendReviewsIndieGamesJoinEOF(self, message: bytes):
        self.fanoutSend(os.getenv('JOIN_INDIE_REV'), message)

    
    def sendToAvgPlaytimeSorter(self, shardingKey: str, message: bytes):
        self.directSend(os.getenv('SORT_AVG_PT'), shardingKey, message)
    def sendAvgPlaytimeSortEOF(self, message: bytes):
        self.fanoutSend(os.getenv('SORT_AVG_PT'), message)

    
    def sendToPositiveReviewsSorter(self, shardingKey: str, message: bytes):
        self.directSend(os.getenv('SORT_INDIE_POS_REV'), shardingKey, message)
    def sendPositiveReviewsSortEOF(self, message: bytes):
        self.fanoutSend(os.getenv('SORT_INDIE_POS_REV'), message)
    

    def sendToNegativeReviewsSorter(self, shardingKey: str, message: bytes):
        self.directSend(os.getenv('SORT_ACT_REV'), shardingKey, message) 
    def sendNegativeReviewsSortEOF(self, message: bytes):
        self.fanoutSend(os.getenv('SORT_ACT_REV'), message)
    
    
