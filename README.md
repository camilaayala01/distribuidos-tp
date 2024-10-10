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

# Descargar datasets 
```
pip install --user kaggle
mkdir ~/.kaggle
cd ~/.kaggle
touch kaggle.json
echo "{"username":"camilaayala01","key":"1a21e47d2d693e4ab96853cad6149bd3"}" > kaggle.json
kaggle datasets download -d fronkongames/steam-games-dataset
kaggle datasets download -d andrewmvd/steam-reviews
mkdir distribuidos
mv ./steam-games-dataset.zip ./distribuidos ; mv ./steam-reviews.zip ./distribuidos
cd distribuidos
unzip steam-games-dataset.zip ; unzip steam-reviews.zip
rm games.json ; rm steam-games-dataset.zip ; rm steam-reviews.zip

```
# Reducir datasets
```
head -n 100 games.csv > games-reducido.csv
head -n 10000 dataset.csv > reviews-reducido.csv
```

# Ejecución
## Prerequisites
Se debe contar con la imagen base. Para descargar esta, se debe correr desde el root
```
./base-images/build.sh
``` 

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

# Correr script para testear el programa
Para correr este script, se debe correr el comando 
```
./comparison.sh <directorio_esperadas> <directorio_obtenidas>
```
En particular, está configurado para correrlo como
```
./comparison.sh client/expectedResponses client/responses
```
pero pueden ubicar los archivos en donde deseen

## Como interpretar los resultados de diff
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

