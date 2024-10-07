#!/bin/bash
docker compose -f docker-compose-rabbit.yaml stop -t 1
docker compose -f docker-compose-rabbit.yaml down