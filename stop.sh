#!/bin/bash
docker compose -f docker-compose-query-1.yaml stop -t 1
docker compose -f docker-compose-query-1.yaml down
