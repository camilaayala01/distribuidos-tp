FROM zeromq-base:0.0.1

# Install golang
RUN apt-get install python3 python3-pip -y
RUN pip install --break-system-packages pyzmq
RUN apt install python3-pika