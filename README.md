<p align="center">
  <img src="img/polito_bot_logo.jpg" alt="PoliTo Mapping Bot" width="600"/>
</p>

# PoliTo-Paths

## Descrizione del progetto

**PoliTo-Paths** è un bot Telegram che aiuta gli utenti a trovare il percorso più semplice tra due aule o punti all’interno del Politecnico di Torino. Il bot guida l’utente passo-passo, mostrando le istruzioni di navigazione e le immagini della mappa, rendendo facile orientarsi anche per chi non conosce bene l’edificio.

### Funzionalità principali

- Selezione del punto di partenza e della destinazione tramite comandi interattivi.
- Navigazione guidata con istruzioni testuali e immagini.
- Interfaccia semplice tramite Telegram.
- Gestione delle conversazioni e possibilità di annullare l’operazione in qualsiasi momento.

---

## Spiegazione dei file principali

| File                | Descrizione                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `run_app.sh`        | Script bash per avviare il bot. Gestisce la creazione/attivazione della virtualenv, installa le dipendenze mancanti e avvia il bot in background. Termina eventuali istanze già attive. Logga gli errori in `app_error.log`. |
| `stop_app.sh`       | Script bash per fermare tutte le istanze attive del bot.                    |
| `telegram.token`    | File di testo che deve contenere il token del bot Telegram fornito da BotFather. |
| `src/main.py`       | Entry point Python dell’applicazione.                                       |
| `src/telegram_bot.py` | Gestisce la logica principale del bot e registra i comandi.                |

---

## Come avviare il bot da terminale

1. **Clona il repository (se non l’hai già fatto):**
   ```bash
   git clone https://github.com/giuuuug/PoliTo-Paths.git
   cd PoliTo-Paths
   ```

2. **Crea il file `telegram.token` nella cartella principale**  
   Inserisci al suo interno il token fornito da BotFather.

3. **Rendi eseguibili gli script bash (solo la prima volta):**
   ```bash
   chmod +x run_app.sh stop_app.sh
   ```

4. **Avvia il bot:**
   ```bash
   ./run_app.sh
   ```
   - Lo script crea e attiva automaticamente la virtualenv `.venv` se non esiste.
   - Installa le dipendenze Python necessarie (`python-telegram-bot`, `psycopg2-binary`).
   - Avvia il bot in background e salva eventuali errori in `app_error.log`.

5. **Per fermare il bot:**
   ```bash
   ./stop_app.sh
   ```

6. **Per vedere i log di errore:**
   ```bash
   cat app_error.log
   ```

---

## Note aggiuntive

- Se il bot non parte, controlla che il file `telegram.token` sia presente e corretto.
- Se hai problemi con la virtualenv, elimina la cartella `.venv` e rilancia `./run_app.sh`.
- Puoi testare il bot cercando **@polito_paths_bot** su Telegram (se il token è quello ufficiale).

---

Se vuoi aggiungere nuove aule o modificare la logica di navigazione, consulta i file Python nella cartella `src/command/` e le query SQL in `src/database/SQL/`.
