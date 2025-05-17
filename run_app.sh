#!/bin/bash

PROJECT_DIR="$(dirname "$(realpath "$0")")"
VENV_DIR="$PROJECT_DIR/.venv"
MAIN_FILE="$PROJECT_DIR/src/main.py" 
APP_NAME="PoliTo Paths"
TOKEN_FILE="$PROJECT_DIR/telegram.token"

cd "$PROJECT_DIR" || exit 1

# Define the log file
LOG_FILE="$PROJECT_DIR/app_error.log"

# Clear the log file at the start of the script
> "$LOG_FILE"

# Funzioni di supporto
info_msg() { echo -e "\033[1;30m$1\033[0m"; }
error_msg() { echo -e "\033[1;31m$1\033[0m" >&2; }
success_msg() { echo -e "\033[1;32m$1\033[0m"; }
warning_msg() { echo -e "\033[1;33m$1\033[0m"; }

# Controlla se il file telegram.token esiste
if [ ! -f "$TOKEN_FILE" ]; then
    error_msg "ERRORE - File 'telegram.token' non trovato."
    error_msg "Crea un file 'telegram.token' (livello root) e incolla il Token Telegram fornito da Botfather."
    exit 1
fi

# Configurazione ambiente
if [ ! -d "$VENV_DIR" ]; then
    info_msg "Creazione di .venv"
    if ! python3 -m venv "$VENV_DIR" 2>/dev/null; then
        info_msg "Installazione pacchetto python3-venv necessaria..."
        sudo apt update && sudo apt install -y python3-venv || {
            error_msg "Installazione python3-venv fallita!"
            exit 1
        }
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

# Controlla se un altro processo è già in esecuzione
EXISTING_PID=$(pgrep -f "python.*$(basename "$MAIN_FILE")")
if [ -n "$EXISTING_PID" ]; then
    warning_msg "Un'altra istanza dell'app è già in esecuzione"
    
    # Prima prova a terminare normalmente
    kill "$EXISTING_PID" 2>/dev/null
    sleep 2
    
    # Se il processo esiste ancora, usa kill -9
    if kill -0 "$EXISTING_PID" 2>/dev/null; then
        error_msg "Terminazione normale fallita."
        warning_msg "Tentativo di terminazione forzata con kill -9..."
        kill -9 "$EXISTING_PID" 2>/dev/null
        sleep 1
        
        # Verifica finale
        if kill -0 "$EXISTING_PID" 2>/dev/null; then
            error_msg "Impossibile terminare il processo esistente. Esci."
            exit 1
        else
            success_msg "Processo terminato forzatamente"
        fi
    else
        success_msg "Processo esistente terminato con successo."
    fi
fi

# Avvia applicazione in background e redirige gli errori in un file di log
nohup python3 "$MAIN_FILE" >/dev/null 2>>"$LOG_FILE" &
PID=$!

# Attesa breve per catturare errori immediati
sleep 2

# Controlla se il processo è ancora attivo
if ! kill -0 $PID 2>/dev/null; then
    error_msg "ERRORE - Il processo è terminato inaspettatamente."
    exit 1
fi

info_msg "$APP_NAME avviato correttamente. PID: $PID"