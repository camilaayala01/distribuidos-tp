#!/bin/bash
docker build -f python-base-rabbitmq.dockerfile -t rabbitmq-python-base:0.0.1 .
docker build -f python-base-zeromq.dockerfile -t zeromq-python-base:0.0.1 .