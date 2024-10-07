FROM zeromq-python-base:0.0.1
COPY . .
CMD python3 ./main.py