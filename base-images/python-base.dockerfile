FROM ubuntu:24.04

# Install golang
RUN apt update && apt install python3 python3-pip -y
RUN apt install python3-pika