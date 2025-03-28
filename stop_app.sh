#!/bin/bash

# Nome dello script Python da fermare (modifica se necessario)
APP_NAME="app.py"

# Cerca tutti i processi Python relativi a app.py e li termina
pids=$(pgrep -f "python3 $APP_NAME")

if [ -z "$pids" ]; then
    echo "Nessun processo attivo trovato per $APP_NAME."
else
    echo "Terminando i processi per $APP_NAME (PIDs: $pids)..."
    kill -9 $pids
    echo "Processi terminati."
fi