#!/bin/bash
docker compose -f docker-compose-dev.yaml stop -t 10
docker compose -f docker-compose-dev.yaml down
