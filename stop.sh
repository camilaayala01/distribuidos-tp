#!/bin/bash
docker compose -f docker-compose-queries.yaml stop -t 1
docker compose -f docker-compose-queries.yaml down
