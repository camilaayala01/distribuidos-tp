#!/bin/bash
docker compose -f docker-compose-query-2.yaml stop -t 1
docker compose -f docker-compose-query-2.yaml down
