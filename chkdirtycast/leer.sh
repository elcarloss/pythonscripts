#!/bin/bash
file="/home/calarcon/pyvirtual/scripts/chkdirtycast/alertas.txt"

while IFS= read -r line
do
    linea=$($line|awk '{print $1}')
    puerto=$($line|awk '{print $2}')
#    echo $linea
    if [ "$linea" != "OK:" ]
    then
        echo "TODO BIEN"
    else
        echo "NO TAN BIEN"
        echo $puerto
    fi
done <"$file"
