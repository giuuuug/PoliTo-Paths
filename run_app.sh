#!/bin/bash

PROJECT_DIR="$(dirname "$(realpath "$0")")"
VENV_DIR="$PROJECT_DIR/.venv"  
LOG_FILE="$PROJECT_DIR/app.log"

cd "$PROJECT_DIR" || exit 1

if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "ERRORE: Virtual environment non trovato in $VENV_DIR!" >> "$LOG_FILE"
    exit 1
fi

nohup python3 app.py >> "$LOG_FILE" 2>&1 &

echo "App avviata in background. PID: $!" 
echo "Logs in: $LOG_FILE"
