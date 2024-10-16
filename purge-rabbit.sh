#!/bin/bash

CONTAINER_NAME="tp1-distribuidos-rabbitmq-1"

queues=$(docker exec "$CONTAINER_NAME" rabbitmqctl list_queues | awk '{print $1}' | tail -n +4)

for queue in $queues; do
    echo "Purging queue: $queue"
    docker exec "$CONTAINER_NAME" rabbitmqctl purge_queue "$queue"
done
