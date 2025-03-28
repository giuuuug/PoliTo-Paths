# PoliTo-Paths

### **How to Start/Stop the Bot**  

#### **Prerequisites**  
- Python 3.12+ installed  
- `git` installed

#### **Steps**  
1. **Clone the repository** (if not already done):  
   ```bash
   git clone https://github.com/giuuuug/PoliTo-Paths.git
   cd PoliTo-Paths
   ```

2. **Open the project with VSCode**  
   - Use `Open Folder` and select the project directory

3. **Set up a virtual environment**  
   <img src="https://github.com/user-attachments/assets/a239616a-c725-4e00-9cf4-a67d81e3dc28" alt="VSCode Python Environment Setup" width="600" align="left" style="margin-right: 20px"/>
   
   - Select the Python extension icon (1)
   - then click on the `+` icon (2) and select the latest Python version when prompted.
   
   <div style="clear: both;"></div>
   
   <br><br><br><br><br><br><br><br><br><br><br><br><br><br>
   
   Open a new terminal (`Terminal → New Terminal`) and install dependencies:
   ```bash
   pip install python-telegram-bot
   ```
   If installed without errors, you're ready to start the bot.

5. **Run the bot**:  
   ```bash
   ./run_app.sh
   ```
   This script will:  
   - Automatically activate the virtual environment (`.venv`)  
   - Start the bot in background (logs saved to `app.log`)  

6. **Stop the bot**:  
   ```bash
   ./stop_app.sh
   ```
   This terminates all running instances of `app.py`

7. **Test the bot**:  
   Search for **@polito_paths_bot** in Telegram

#### **Troubleshooting**  
- **If `run_app.sh` fails**:  
  - Verify `.venv` exists (repeat Step 3)  
  - Ensure execute permissions:  
    ```bash
    chmod +x run_app.sh stop_app.sh
    ```  
- Check `app.log` for error details

### **Key Files**  
| File          | Purpose                                |  
|---------------|----------------------------------------|  
| `run_app.sh`  | Starts the bot with auto-venv check    |  
| `stop_app.sh` | Stops all bot instances                |  
| `app.log`     | Contains runtime logs                  |
