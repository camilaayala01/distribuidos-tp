#!/bin/bash
docker compose -f docker-compose-query-4.yaml stop -t 1
docker compose -f docker-compose-query-4.yaml down
