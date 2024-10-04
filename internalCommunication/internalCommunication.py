import pika
import signal
import os

PREFETCH_COUNT = 1 # break round robin
DELIVERY_MODE = 1 # make message transient, doesn't matter yet

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
        result = self._channel.queue_declare(queue='', auto_delete = True) # CHANGE IN PRODUCTION, JUST FOR TESTING
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
        # Don't recover connections closed by server
        except pika.exceptions.ConnectionClosedByBroker:
            pass
    

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
        

    def directSend(self, exchangeName: str, routingKey: str, message: bytes):
        self._channel.exchange_declare(exchange=exchangeName, exchange_type='direct')
        self._channel.basic_publish(exchange=exchangeName, routing_key=routingKey, body=message)

    # Query 1

    def sendToOSCountsGrouper(self, message: bytes):
        self.basicSend(os.getenv('GROUP_OS'), message)

    def sendToOSCountsJoiner(self, message: bytes): #UNO SOLO
        self.basicSend(os.getenv('JOIN_OS'), message)


    # Query 2

    def sendToIndieFilter(self, message: bytes):
        self.basicSend(os.getenv('FILT_INDIE'), message)

    def sendToDecadeFilter(self, message: bytes):
        self.basicSend(os.getenv('FILT_DEC'), message)

    def sendToAvgPlaytimeSorter(self, shardingKey: str, message: bytes):
        self.directSend(os.getenv('SORT_AVG_PT'), shardingKey, message)

    def sendToAvgPlaytimeSorterConsolidator(self, message: bytes):
        self.basicSend(os.getenv('CONS_SORT_AVG_PT'), message)



    # Query 3

    def sendToNegativeReviewsGrouper(self, message: bytes):
        self.basicSend(os.getenv('GROUP_NEG_REV'), message)

    def sendToReviewsIndieGamesJoiner(self, shardingKey: str, message: bytes):
        self.directSend(os.getenv('JOIN_INDIE_REV'), shardingKey, message)



    def sendToActionFilter(self, message: bytes):
        self.basicSend(os.getenv('FILT_ACT'), message)
    
    

    
    
    def sentToEnglishFilter(self, message: bytes):
        self.basicSend(os.getenv('FILT_ENG'), message)
        
    def sendToPositiveReviewsGrouper(self, message: bytes):
        self.basicSend(os.getenv('GROUP_POS_REV'), message)

    

    
        
    
 
    def sendToPositiveReviewsActionGamesJoiner(self, shardingKey: str, message: bytes):
        self.directSend(os.getenv('JOIN_ACT_POS_REV'), shardingKey, message)

    def sendToNegativeReviewsActionGamesJoiner(self, shardingKey: str, message: bytes):
        self.directSend(os.getenv('JOIN_ACT_NEG_REV'), shardingKey, message)

   
    
    def sendToReviewsIndieGamesConsolidator(self, message: bytes):
        self.basicSend(os.getenv('CONS_JOIN_INDIE_REV'), message)
    
    

    def sendToPositiveReviewsSorter(self, shardingKey: str, message: bytes):
        self.directSend(os.getenv('SORT_INDIE_POS_REV'), shardingKey, message)

    def sendToPositiveReviewsSorterConsolidator(self, message: bytes):
         self.basicSend(os.getenv('CONS_SORT_INIDIE_POS_REV'), message)

    def sendToNegativeReviewsSorter(self, message: bytes): #el de percentil noventa
        self.basicSend(os.getenv('SORT_ACT_NEG_REV'), message)

    def sendToEnglishReviewsJoinerConsolidator(self, message: bytes):
        self.basicSend(os.getenv('CONS_POS_REV_EN_JOINER'), message) 

    def sendToDispatcher(self, message: bytes):
        self.basicSend(os.getenv('RESP_DISP'), message)

    

    
 
    
    
