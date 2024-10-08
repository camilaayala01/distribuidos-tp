#!/bin/bash
docker compose -f docker-compose-queries.yaml stop -t 25
docker compose -f docker-compose-queries.yaml down
