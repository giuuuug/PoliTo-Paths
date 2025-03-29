#!/bin/bash

PROJECT_DIR="$(dirname "$(realpath "$0")")"
VENV_DIR="$PROJECT_DIR/.venv"
MAIN_FILE="$PROJECT_DIR/src/main.py" 
LOG_FILE="$PROJECT_DIR/app.log"
APP_NAME="PoliTo Paths"

# Svuota il file di log all'avvio
> "$LOG_FILE"

cd "$PROJECT_DIR" || exit 1

# Funzioni di supporto
info_msg() { echo -e "\033[1;30m$1\033[0m"; }
error_msg() { echo -e "\033[1;31m$1\033[0m" >&2; }
success_msg() { echo -e "\033[1;32m$1\033[0m"; }
warning_msg() { echo -e "\033[1;33m$1\033[0m"; }

# Configurazione ambiente
if [ ! -d "$VENV_DIR" ]; then
    # Prima prova a creare il virtualenv normalmente
    info_msg "Creazione di .venv"
    if ! python3 -m venv "$VENV_DIR" 2>/dev/null; then
        info_msg "Installazione pacchetto python3-venv necessaria..."
        sudo apt update && sudo apt install -y python3-venv || {
            error_msg "Installazione python3-venv fallita!"
            exit 1
        }
        # Secondo tentativo dopo l'installazione
        info_msg "Nuovo tentativo. Creazione di .venv"
        python3 -m venv "$VENV_DIR" || {
            error_msg "Creazione venv fallita dopo installazione pacchetto"
            exit 1
        }
    fi
    
    info_msg "Attivazione della .venv"
    source "$VENV_DIR/bin/activate"
    info_msg "Installazione pacchetti [python-telegram-bot] [psycopg2] mancanti..."
    pip install -q python-telegram-bot psycopg2-binary || {
        error_msg "Installazione dipendenze fallita"
        exit 1
    }
    success_msg "OK! .venv attivata"
else
    source "$VENV_DIR/bin/activate"
fi

# Termina processi esistenti
pkill -f "python.*$(basename "$MAIN_FILE")"

# Avvia applicazione scrivendo solo sul log
nohup python3 "$MAIN_FILE" >> "$LOG_FILE" 2>&1 &
PID=$!

# Attesa breve per catturare errori immediati
sleep 2

# Controlla se il processo è ancora attivo
if ! kill -0 $PID 2>/dev/null; then
    error_msg "ERRORE - Processo terminato. Contenuto in app.log"
    #cat "$LOG_FILE"
    exit 1
fi

# Controlla se è stato scritto qualcosa nel log
if [ -s "$LOG_FILE" ]; then
    error_msg "ERRORE - Output non previsto in app.log"
    #cat "$LOG_FILE"
    kill -9 $PID
    exit 1
fi

success_msg "$APP_NAME avviato correttamente. PID: $PID"