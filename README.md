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

## Query 1 
windows: u8, mac: u8, linux: u8
    GrouperOSCounts
windowsParcialCount: u32, macParcialCount: u32, linuxParcialCount: u32
    JoinerOSCount (solo uno)
windowsCount: u32, macCount: u32, linux: u32

## Query 2
appID: str, name: str, genres: str, releaseDate: str, avgPlaytime: u32
    FiltererIndie
name: str, releaseDate: str, avgPlaytime: u32
    FiltererDate
name: str, avgPlaytime: u32
    SorterByAvgPlaytime (dispatching por fragment number) si es un end of file se lo manda a todos
10 o menos (name: str) por cada  sorter
    SorterJoinerByAvgPlaytime
10 o menos(name: str)

## Query 3
Tabla reviews:                               Tabla games:
    appid de tabla reviews                          appID: str, name: str, genres: str, releaseDate: str, avgPlaytime: u32
        GrouperIndiePositiveReviews                          FiltererIndie     
    appid: str, parcial count: u32          name: str, releaseDate: str, avgPlaytime: u32
                                JoinerPositiveReviews












