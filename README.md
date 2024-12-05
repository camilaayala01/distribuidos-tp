# distribuidos-tp
Trabajo Practico para la materia Sistemas Distribuidos (7574). 
Integrantes: Noah Masri 108814, Tomas Danko 107431, Camila Ayala 107440
# Descarga de datasets
## Configurar cuenta kaggle
```
pip install --user kaggle
mkdir ~/.kaggle
cd ~/.kaggle
touch kaggle.json
echo "{"username":"camilaayala01","key":"1a21e47d2d693e4ab96853cad6149bd3"}" > kaggle.json
mkdir distribuidos
```
## Descargar datasets completos
```
kaggle datasets download -d camilaayala01/queries-responses
mv ./queries-responses.zip ./distribuidos
cd distribuidos
unzip queries-responses.zip
```
## Descargar datasets reducidos
```
kaggle datasets download -d camilaayala01/distribuidos-tp
mkdir distribuidos/reducido
mv ./distribuidos-tp.zip ./distribuidos/reducido
cd distribuidos/reducido
unzip distribuidos-tp.zip
```
# Ejecución
## Prerequisites
Se debe contar con la imagen base. Para descargar esta, se debe correr desde el root
```
./base-images/build.sh
``` 
Se debe contar a su vez con un archivo docker-compose-dev.yaml. Este puede ser generador a través del script de generación.

## Generación del compose
Para generar un compose, se debe correr 
```
generate-compose <output-path> <cantidad-clientes>
```
En caso de querer cambiar la cantidad de nodos específicos de algún tipo, se debe modificar el contenido del archivo `compose.env`
En caso de elegir un output path que no sea `docker-compose-dev.yaml`, se debe modificar el script de corrida (`run.sh`) y el de frenada del programa (`stop.sh`).
## Para ejecutar todas las queries
En primer lugar, se debe activar rabbit. Esto se hace corriendo desde el root el script de rabbit
```
./run-rabbit.sh
```
Una vez que este está prendido, ahora sí se debe correr a las otras querys, ejecutando el script
```
./run.sh
```
Cuando se desee que se frene la ejecución, se debe correr:
* Para cortar rabbit: `./stop-rabbit.sh`
* Para cortar los nodos y el cliente: `./stop.sh`
## Multiples ejecuciones de un cliente
Una vez generado en compose se puede apreciar que cada cliente tiene una variable de entorno `AMOUNT_OF_EXECUTIONS` mediante la cual se puede configurar cuantas veces el cliente se ejecuta 
## Correr con distintos dataset
En el compose en el cliente se tiene tambien las variable de entorno `REVIEWS_STORAGE_FILEPATH` y `GAMES_STORAGE_FILEPATH` en las cuales se puede configurar respectivamente sobre que dataset se ejecutara el programa. 
En caso de querer correrlo con el dataset completo el valor seria:

```
    REVIEWS_STORAGE_FILEPATH=./datasets/reviews.csv
    GAMES_STORAGE_FILEPATH=./datasets/games.csv
```

y de querer correrlo con el reducido seria:

```
    REVIEWS_STORAGE_FILEPATH=./datasets/reducido/reviews-reducido.csv
    GAMES_STORAGE_FILEPATH=./datasets/reducido/games-reducido.csv
```
# Para borrar las carpetas
Si se quierer borrar las carpetas correspondientes a los volumenes se puede ejecutar el siguiente script:
```
sudo delete-files.sh
```
# Correr script para testear el programa
Para correr este script, se debe correr el comando 
```
./comparison.sh <directorio_esperadas> <directorio_obtenidas>
```
En particular, está configurado para correrlo como
```
./comparison.sh ~/.kaggle/distribuidos client-{clientnumber}/responses/exec-{exec-number}
```

o en caso de ser el reducido seria
```
./comparison.sh ~/.kaggle/distribuidos/reducido client-{clientnumber}/responses/exec-{exec-number}
```
pero pueden ubicar los archivos en donde deseen


## Como interpretar los resultados de las querys 4 y 5
Si se obtiene un mensaje como
```
12c12
< Viejo contenido
---
> Nuevo contenido
```
Implica que entre un archivo y el otro, en la línea 12 hay diferencias. El 'viejo contenido' en nuestro caso es el archivo de respuestas esperadas, mientras que el 'nuevo contenido' son las respuestas obtenidas. 

Luego, el mensaje
```
11a12
> Nuevo contenido
```
implica que al contenido del archivo original se le agregó una nueva línea. No son muy relevantes los números que dice, ya que pueden ser confusos, pero sí implica que se agregó algo.

Por último, el mensaje
```
11d12
< Viejo contenido
```
implica que al contenido del archivo original se le eliminó una línea.


