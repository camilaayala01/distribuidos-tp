#!/bin/bash

# Archivos de texto de entrada
archivo1="client/expectedResponses/query1.txt"
archivo2="client/responses/query1.txt"

# Función para extraer números basados en la línea que corresponde
function extraer_numero {
    grep "$1" "$2" | awk '{print $NF}'
}

# Extraer los números de las líneas correspondientes
total_juegos1=$(extraer_numero "Total de juegos: " "$archivo1")
total_juegos2=$(extraer_numero "Total de juegos: " "$archivo2")

total_windows1=$(extraer_numero "Total de juegos soportados en Windows: " "$archivo1")
total_windows2=$(extraer_numero "Total de juegos soportados en Windows: " "$archivo2")

total_linux1=$(extraer_numero "Total de juegos soportados en Linux: " "$archivo1")
total_linux2=$(extraer_numero "Total de juegos soportados en Linux: " "$archivo2")

total_mac1=$(extraer_numero "Total de juegos soportados en Mac: " "$archivo1")
total_mac2=$(extraer_numero "Total de juegos soportados en Mac: " "$archivo2")

# Función para imprimir en colores
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

# Función para comparar y mostrar resultados
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

echo_color "azul" "--Comparando Query 1--"

# Comparaciones
comparar_total "" "$total_juegos1" "$total_juegos2"
comparar_total " soportados en Windows" "$total_windows1" "$total_windows2"
comparar_total " soportados en Linux" "$total_linux1" "$total_linux2"
comparar_total " soportados en Mac" "$total_mac1" "$total_mac2"