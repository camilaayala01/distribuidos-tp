FROM ubuntu:24.04

RUN apt update && apt install python3 python3-pip -y
RUN apt install python3-pika
RUN pip install --break-system-packages langid
