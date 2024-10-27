#!/bin/bash
#echo "Nombre del archivo de salida: $1"
echo "Cantidad de clientes: $1"
python3 compose-generator.py "docker-compose-test.yaml" $1