#!/bin/bash

PROJECT_DIR="$(dirname "$(realpath "$0")")"
MAIN_FILE="$PROJECT_DIR/src/main.py"
APP_NAME="PoliTo Paths"

# Funzioni di supporto
error_msg() {
    echo -e "\033[1;31m$1\033[0m" >&2
}

success_msg() {
    echo -e "\033[1;32m$1\033[0m"
}

warning_msg() {
    echo -e "\033[1;33m$1\033[0m"
}

# Cerca processi attivi
pids=$(pgrep -f "python3.*$(basename "$MAIN_FILE")")

if [ -z "$pids" ]; then
    error_msg "Nessun processo attivo trovato per $APP_NAME."
else
    warning_msg "Processi attivi trovati (PIDs: $pids). Terminazione forzata..."
    kill -9 $pids 2>/dev/null
    
    # Verifica finale
    sleep 0.5
    if pgrep -f "python3.*$(basename "$MAIN_FILE")" >/dev/null; then
        error_msg "Impossibile terminare tutti i processi!"
        exit 1
    else
        success_msg "$APP_NAME arrestato con successo."
    fi
fi