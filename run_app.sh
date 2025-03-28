#!/bin/bash

# Percorso assoluto della cartella del progetto (modifica se necessario)
PROJECT_DIR="$(dirname "$(realpath "$0")")"
VENV_DIR="$PROJECT_DIR/.venv"  # Assumendo che la venv si chiami "venv" ed è nella root
LOG_FILE="$PROJECT_DIR/app.log"

# Entra nella cartella del progetto
cd "$PROJECT_DIR" || exit 1

# Attiva la venv (se esiste)
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "ERRORE: Virtual environment non trovato in $VENV_DIR!" >> "$LOG_FILE"
    exit 1
fi

# Esegui l'app in background e scrivi i log, ignorando il segnale HUP (disconnessione SSH)
nohup python3 app.py >> "$LOG_FILE" 2>&1 &

echo "App avviata in background. PID: $!" 
echo "Logs in: $LOG_FILE"
