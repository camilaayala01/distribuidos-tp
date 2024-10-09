#!/bin/bash
docker compose -f docker-compose-queries.yaml stop -t 10
docker compose -f docker-compose-queries.yaml down
