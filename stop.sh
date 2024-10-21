#!/bin/bash
docker compose -f docker-compose-test.yaml stop -t 10
docker compose -f docker-compose-test.yaml down
docker image prune
