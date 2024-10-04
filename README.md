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
echo "{"username":"camilaayala01","key":"1a21e47d2d693e4ab96853cad6149bd3"}" > kaggle.js
kaggle datasets download -d fronkongames/steam-games-dataset
kaggle datasets download -d andrewmvd/steam-reviews
mkdir distribuidos
mv ./steam-games-dataset.zip ./distribuidos && mv ./steam-reviews.zip ./distribuidos
cd distribuidos
unzip steam-games-dataset.zip && unzip steam-reviews.zip
rm games.json && rm steam-games-dataset.zip && rm steam-reviews.zip

```
