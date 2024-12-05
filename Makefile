SHELL := /bin/bash
CONTAINER_NAME := distribuidos-tp-rabbitmq-1

run-rabbit:
	docker compose -f docker-compose-rabbit.yaml up --build
.PHONY: run-rabbit

stop-rabbit:
	docker compose -f docker-compose-rabbit.yaml stop -t 1
	docker compose -f docker-compose-rabbit.yaml down
.PHONY: stop-rabbit

purge-queues:
	@queues=$$(docker exec "$(CONTAINER_NAME)" rabbitmqctl list_queues | awk '{print $$1}' | tail -n +4); \
	for queue in $$queues; do \
		echo "Purging queue: $$queue"; \
		docker exec "$(CONTAINER_NAME)" rabbitmqctl purge_queue "$$queue"; \
	done
.PHONY: purge-queues

run:
	docker compose -f docker-compose-dev.yaml up --build
.PHONY: run

stop:
	docker compose -f docker-compose-dev.yaml stop -t 10
	docker compose -f docker-compose-dev.yaml down
	docker image prune -f
.PHONY: stop

destroy:
	docker compose -f docker-compose-dev.yaml stop -t 10
	docker compose -f docker-compose-dev.yaml down
	docker image prune -f
	@queues=$$(docker exec "$(CONTAINER_NAME)" rabbitmqctl list_queues | awk '{print $$1}' | tail -n +4); \
	for queue in $$queues; do \
		echo "Purging queue: $$queue"; \
		docker exec "$(CONTAINER_NAME)" rabbitmqctl purge_queue "$$queue"; \
	done
	sudo rm -rf aggregator/Aggregator*/
	sudo rm -rf sorter/Consolidator*/
	sudo rm -rf sorter/Sorter*/
	sudo rm -rf joiner/Joiner*/
	sudo rm -rf client-*/
	sudo rm -rf borderNode/data/
	sudo rm -rf initializer/clients/
.PHONY: destroy