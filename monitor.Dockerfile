FROM rabbitmq-python-base:0.0.1
RUN apt-get update && \
    apt-get -qy full-upgrade && \
    apt-get install -qy curl && \
    apt-get install -qy curl && \
    curl -sSL https://get.docker.com/ | sh
COPY . .
ENTRYPOINT ["python3", "/main.py"]
