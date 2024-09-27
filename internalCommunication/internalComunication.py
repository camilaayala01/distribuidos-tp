import pika
import signal
PREFETCH_COUNT = 1
HOST = 'rabbitmq'

class InternalCommunication:
    def __init__(self, name: str):
        self._executerName = name
        self._connection = self.startConnection()
        self._channel = self.createChannel()

    def startConnection(self) -> pika.BlockingConnection:
        signal.signal(signal.SIGTERM, self.stop)
        return pika.BlockingConnection(
        pika.ConnectionParameters(host=HOST))

    def createChannel(self) -> pika.adapters.blocking_connection.BlockingChannel:
        channel = self._connection.channel()
        channel.basic_qos(prefetch_count=PREFETCH_COUNT)
        return channel

    def defineMessageHandler(self, callback):
        self._channel.queue_declare(queue=self._executerName)
        self._channel.basic_consume(queue=self._executerName, on_message_callback=callback)
        try:
            self._channel.start_consuming() 
        # Don't recover connections closed by server
        except pika.exceptions.ConnectionClosedByBroker:
            pass
    
    def readFromQueue(self) -> bytes | None :
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
                delivery_mode=1,  # make message transient, es lo mismo por ahora
            ))
        
    
    def fanoutSend(self, exchangeName: str, message: bytes):
        self._channel.exchange_declare(exchange=exchangeName, exchange_type='fanout')
        self._channel.basic_publish(exchange=exchangeName, routing_key='', body=message)

    # el exchange va a mandar los mensajes a solo los que estan conectados a ese routing key
    def directSend(self, exchangeName: str, routingKey: str, message: bytes):
        self._channel.exchange_declare(exchange=exchangeName, exchange_type='direct')
        self._channel.basic_publish(exchange=exchangeName, routing_key=routingKey, body=message)


    def sendToActionFilter(self, message: bytes):
        self.basicSend('actionFilter', message)
    
    def sendToIndieFilter(self, message: bytes):
        self.basicSend('indieFilter', message)

    def sendToDecadeFilter(self, message: bytes):
        self.basicSend('decadeFilter', message)
    
    def sentToEnglishFilter(self, message: bytes):
        self.basicSend('englishFilter', message)
        
    def sendToPositiveReviewsGrouper(self, message: bytes):
        self.basicSend('positiveReviewsGrouper', message)

    def sendToNegativeReviewsGrouper(self, message: bytes):
        self.basicSend('negativeReviewsGrouper', message)

    def sendToOSCountsGrouper(self, message: bytes):
        self.basicSend('OSCountsGrouper', message)
        
    def sendToOSCountsJoiner(self, shardingKey: str, message: bytes):
        self.directSend('OSCountsJoiner', shardingKey, message)
    def sendOSCountsJoinEOF(self, message: bytes):
        self.fanoutSend('OSCountsJoiner', message)
    
    def sendToPositiveReviewsActionGamesJoiner(self, shardingKey: str, message: bytes):
        self.directSend('positiveReviewsActionGamesJoiner', shardingKey, message)
    def sendPositiveReviewsActionGamesJoinEOF(self, message: bytes):
        self.fanoutSend('positiveReviewAsctionGamesJoiner', message)

    def sendToNegativeReviewsActionGamesJoiner(self, shardingKey: str, message: bytes):
        self.directSend('negativeReviewAsctionGamesJoiner', shardingKey, message)
    def sendNegativeReviewsActionGamesJoinEOF(self, message: bytes):
        self.fanoutSend('negativeReviewAsctionGamesJoiner', message)


    def sendToReviewsIndieGamesJoiner(self, shardingKey: str, message: bytes):
        self.directSend('reviewsIndieGameJoiner', shardingKey, message)
    def sendReviewsIndieGamesJoinEOF(self, message: bytes):
        self.fanoutSend('reviewsIndieGamesJoiner', message)

    
    def sendToAvgPlaytimeSorter(self, shardingKey: str, message: bytes):
        self.directSend('avgPlaytimeSorter', shardingKey, message)
    def sendAvgPlaytimeSortEOF(self, message: bytes):
        self.fanoutSend('avgPlaytimeSorter', message)

    
    def sendToPositiveReviewsSorter(self, shardingKey: str, message: bytes):
        self.directSend('positiveReviewsSorter', shardingKey, message)
    def sendPositiveReviewsSortEOF(self, message: bytes):
        self.fanoutSend('positiveReviewsSorter', message)
    

    def sendToNegativeReviewsSorter(self, shardingKey: str, message: bytes):
        self.directSend('negativeReviewsSorter', shardingKey, message) 
    def sendNegativeReviewsSortEOF(self, message: bytes):
        self.fanoutSend('negativeReviewsSorter', message)
    
    
