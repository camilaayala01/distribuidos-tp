#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <directorio_esperadas> <directorio_obtenidas>"
    exit 1
fi

directorio_esperadas="$1"
directorio_obtenidas="$2"

function echo_color {
    color=$1
    texto=$2
    case $color in
        "rojo")
            echo -e "\e[31m$texto\e[0m"
            ;;
        "verde")
            echo -e "\e[32m$texto\e[0m"
            ;;
        "amarillo")
            echo -e "\e[33m$texto\e[0m"
            ;;
        "azul")
            echo -e "\e[34m$texto\e[0m"
            ;;
        *)
            echo "$texto"
            ;;
    esac
}

# query 1

q1_esperadas="${directorio_esperadas}/query1.txt"
q1_obtenidas="${directorio_obtenidas}/query1.txt"

function extraer_numero {
    grep "$1" "$2" | awk '{print $NF}'
}

total_juegos1=$(extraer_numero "Total de juegos: " "$q1_esperadas")
total_juegos2=$(extraer_numero "Total de juegos: " "$q1_obtenidas")

total_windows1=$(extraer_numero "Total de juegos soportados en Windows: " "$q1_esperadas")
total_windows2=$(extraer_numero "Total de juegos soportados en Windows: " "$q1_obtenidas")

total_linux1=$(extraer_numero "Total de juegos soportados en Linux: " "$q1_esperadas")
total_linux2=$(extraer_numero "Total de juegos soportados en Linux: " "$q1_obtenidas")

total_mac1=$(extraer_numero "Total de juegos soportados en Mac: " "$q1_esperadas")
total_mac2=$(extraer_numero "Total de juegos soportados en Mac: " "$q1_obtenidas")

function comparar_total {
    local categoria=$1
    local valor1=$2
    local valor2=$3

    if [ -z "$valor1" ] || [ -z "$valor2" ]; then
        echo_color "rojo" "- No se encontró el total de juegos$categoria en uno o ambos archivos."
        return
    fi

    if [ "$valor1" -eq "$valor2" ]; then
        echo_color "verde" "+ Total de juegos$categoria es igual: $valor1."
    else
        echo_color "rojo" "- Total de juegos$categoria es diferente."
        echo_color "amarillo" "- Esperados: $valor1"
        echo_color "amarillo" "- Obtenidos: $valor2"
    fi
}

echo_color "azul" "--Comparando resultados Query 1--"

comparar_total "" "$total_juegos1" "$total_juegos2"
comparar_total " soportados en Windows" "$total_windows1" "$total_windows2"
comparar_total " soportados en Linux" "$total_linux1" "$total_linux2"
comparar_total " soportados en Mac" "$total_mac1" "$total_mac2"
echo

# query 2

comparar_archivos() {
    archivo_esperado="$1"
    archivo_obtenido="$2"

    diferencias=0

    while IFS= read -r expected || [ -n "$expected" ]; do
        IFS= read -r gotten <&3 || [ -n "$gotten" ]

        if [ "$expected" != "$gotten" ]; then
            echo_color "rojo" "La línea difiere"
            echo_color "amarillo" "+ Esperado: $expected"
            echo_color "amarillo" "- Obtenido: $gotten"
            diferencias=1
        fi
    done <"$archivo_esperado" 3<"$archivo_obtenido"

    if [ "$diferencias" -eq 0 ]; then
        echo_color "verde" "Ambos archivos son iguales.\n"
    fi
}

q2_esperadas="${directorio_esperadas}/query2.csv"
q2_obtenidas="${directorio_obtenidas}/query2.csv"

echo_color "azul" "--Comparando Resultados Query 2--"
comparar_archivos "$q2_esperadas" "$q2_obtenidas"

# query 3

q3_esperadas="${directorio_esperadas}/query3.csv"
q3_obtenidas="${directorio_obtenidas}/query3.csv"

echo_color "azul" "--Comparando Resultados Query 3--"
comparar_archivos "$q3_esperadas" "$q3_obtenidas"

# query 4

q4_esperadas="${directorio_esperadas}/query4.csv"
q4_obtenidas="${directorio_obtenidas}/query4.csv"

echo_color "azul" "--Comparando Resultados Query 4--"

sort "$q4_esperadas" > esperadas_ordenado.csv
sort "$q4_obtenidas" > obtenidas_ordenado.csv

diferencias=$(diff esperadas_ordenado.csv obtenidas_ordenado.csv)

if [ -z "$diferencias" ]; then
    echo_color "verde" "Ambos archivos son iguales."
else
    echo_color "rojo" "Los archivos de respuestas difieren: (izq esperado, derecha obtenido)"
    echo_color "amarillo" "$diferencias"
fi

rm esperadas_ordenado.csv obtenidas_ordenado.csv