import pika
import signal
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
        except: # cambiar 
            logging.info(f'action: gracefully shutting down | result: success')

    def stop(self):
        self._channel.stop_consuming()
        self._channel.close()
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

    # indie filter comes here

    def sendToIndiePositiveReviewsGrouper(self, message: bytes):
        self.basicSend(os.getenv('GROUP_INDIE_POS_REV'), message)

    def sendToIndiePositiveReviewsJoiner(self, shardingKey: str, message: bytes):
        self.directSend(os.getenv('JOIN_INDIE_POS_REV'), shardingKey, message)

    def sendToIndiePositiveReviewsConsolidator(self, message: bytes):
        self.basicSend(os.getenv('CONS_JOIN_INDIE_POS_REV'), message)

    def sendToPositiveReviewsSorter(self, shardingKey: str, message: bytes):
        self.directSend(os.getenv('SORT_INDIE_POS_REV'), shardingKey, message)

    def sendToPositiveReviewsSorterConsolidator(self, message: bytes):
         self.basicSend(os.getenv('CONS_SORT_INDIE_POS_REV'), message)


    # Query 4
    
    def sendToActionFilter(self, message: bytes):
        self.basicSend(os.getenv('FILT_ACT'), message)

    def sendToActionNegativeReviewsEnglishJoiner(self, shardingKey: str, message: bytes):
        self.directSend(os.getenv('JOIN_ENG_NEG_REV'), shardingKey, message)
    
    def sendToEnglishFilter(self, message: bytes):
        self.basicSend(os.getenv('FILT_ENG'), message)

    def sendToEnglishNegativeReviewsGrouper(self, message: bytes):
        self.basicSend(os.getenv('GROUP_ENG_NEG_REV'), message)

    def sendToEnglishReviewsJoinerConsolidator(self, message: bytes):
        self.basicSend(os.getenv('CONS_JOIN_ENG_NEG_REV'), message) 

    def sendToEnglishNegativeReviewsCounter(self, shardingKey: str, message: bytes):
        self.directSend(os.getenv('JOIN_ENG_COUNT_MORE_REV'), shardingKey, message)

    def sendToStreamJoinerConsolidator(self, message: bytes):
        self.basicSend(os.getenv('CONS_JOIN_STREAM'), message)

        
    # Query 5

    # action filter comes here, goes to joiner

    def sendToActionAllNegativeReviewsGrouper(self, message: bytes):
        self.basicSend(os.getenv('GROUP_PERC_NEG_REV'), message)
    
    def sendToActionNegativeReviewsJoiner(self,  shardingKey: str, message: bytes):
        self.directSend(os.getenv('JOIN_PERC_NEG_REV'), shardingKey, message)
    
    def sendToActionPercentileSorterConsolidator(self, message: bytes): 
        self.basicSend(os.getenv('CONS_SORT_PERC_NEG_REV'), message)

    
    #End

    def sendToDispatcher(self, message: bytes):
        self.basicSend(os.getenv('RESP_DISP'), message)

    def sendToInitializer(self, message: bytes):
        self.basicSend(os.getenv('INIT'), message)