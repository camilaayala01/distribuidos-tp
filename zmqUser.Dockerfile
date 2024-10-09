FROM zeromq-python-base:0.0.1
COPY . .
ENTRYPOINT ["python3", "/main.py"]