# distribuidos-tp
Trabajo Practico para la materia Sistemas Distribuidos (7574). 

La primera vez correr: base-images/build.sh

## Ejecución de los tests
Para ejecutar los tests unitarios creados para todos los módulos, correr el comando:
```
./run-test.sh
```
Si recibe un warning que dice `bash: ./run-test.sh: Permission denied`, probablemente sea porque no tiene permisos de ejecución sobre el script. Para otorgarse estos permisos, debe correr:
```
chmod +x run-test.sh
```
y luego volver a correr el script